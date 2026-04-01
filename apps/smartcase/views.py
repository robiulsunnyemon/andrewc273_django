import base64
import os
from rest_framework.permissions import IsAuthenticated
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from httpx import request
import openai
from django.conf import settings

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from rest_framework import permissions
from rest_framework.permissions import  AllowAny
from rest_framework.permissions import IsAuthenticatedOrReadOnly


# from apps.smartcase import permissions
from apps.smartcase.permissions import IsOwnerOrReadOnly

from .models import CaseSubmission, CaseDocument
from .serializers import CaseCardMediaSerializer, CaseCardSerializer, CaseSubmissionSerializer, CaseDocumentSerializer
from django.db.models import Q, Count
from rest_framework.pagination import PageNumberPagination

client = openai.OpenAI(api_key=settings.OPEN_AI_API_KEY)

def enhance_case_text(user_text):
    """
    AI Analysis using OpenAI GPT-4o with Retry Logic (Similar to your dental app)
    """
    max_retries = 3
    
    
    PROMPT = """
    Act as a professional editor. Your goal is to fix the grammar, spelling, and flow of the provided text to make it sound professional yet concise.

RAW USER TEXT: "{user_text}"

INSTRUCTIONS:
1. Fix all grammatical and spelling errors (e.g., change "theis" to "this").
2. Make the sentence structure smooth and professional.
3. Keep the original meaning but make it sound more polished.
4. Do NOT add unnecessary legal sections unless the input text is actually a legal case.
5. Respond ONLY in JSON format.

JSON STRUCTURE:
{{
    "status": "success",
    "enhanced_text": "Your polished and corrected version here...",
    "summary": "List of corrections made."
}}
    """

    for attempt in range(max_retries):
        try:
            if not settings.OPEN_AI_API_KEY:
                return {"error": "API Key missing", "status": "failed"}

            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": PROMPT},
                    {"role": "user", "content": user_text}
                ],
                response_format={"type": "json_object"},
                temperature=0, 
                timeout=30
            )
            
            import json
            return json.loads(response.choices[0].message.content)

        except Exception as e:
            if attempt == max_retries - 1:
                return {"error": str(e), "status": "failed"}
            continue # 


def analyze_case_link(link_url):
    """
    OpenAI GPT-4o  (Retry Logic Similar to your dental app) for analyzing legal case links
    """
    max_retries = 3
    LINK_PROMPT = "Analyze this URL and provide a concise legal summary of the document or webpage content. Format your response as a JSON object with 'summary' and 'status' keys."

    for attempt in range(max_retries):
        try:
            
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": LINK_PROMPT},
                    {"role": "user", "content": f"Analyze this link: {link_url}"}
                ],
                response_format={"type": "json_object"},
                temperature=0
            )
            import json
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            if attempt == max_retries - 1:
                return {"summary": "Analysis failed", "status": "failed", "error": str(e)}
            continue

class AIEnhanceTextView(APIView):
    def get(self, request):
        test_text = "theis name is al"
        ai_response = enhance_case_text(test_text)
        return Response(ai_response, status=status.HTTP_200_OK)
    
    def post(self, request):
        user_text = request.data.get('text', '')
        if not user_text:
            return Response({"error": "No text provided"}, status=400)

        ai_response = enhance_case_text(user_text)
        
        return Response(ai_response, status=status.HTTP_200_OK)
   
class AIAnalyzeLinkView(APIView):
    def get (self, request):
        return Response({"message": "Send a POST request with 'link' to analyze."},status=status.HTTP_200_OK)   
    def post(self, request):
     
        link = request.data.get('link', '')
        
        if not link:
            return Response({"error": "No link provided"}, status=status.HTTP_400_BAD_REQUEST)

        ai_response = analyze_case_link(link)
        
        return Response(ai_response, status=status.HTTP_200_OK)
        



class DownloadDocumentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, document_id):
        document = get_object_or_404(CaseDocument, id=document_id)
        # File path theke open kora
        file_handle = document.file.open()
        response = FileResponse(file_handle, as_attachment=True)
        
        # Download file name set kora (Title + original extension)
        ext = os.path.splitext(document.file.name)[1]
        download_name = f"{document.title or 'document'}{ext}"
        response['Content-Disposition'] = f'attachment; filename="{download_name}"'
        return response

class CaseSubmissionListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]
   
    def get(self, request):
        
        search_query = request.query_params.get("search", "").strip()
        #cases = CaseSubmission.objects.all().order_by('-created_at')
        cases = CaseSubmission.objects.filter(user=request.user).order_by('-created_at')
        

        if search_query:
            cases = cases.filter(
            Q(case_title__icontains=search_query) | 
            Q(case_number__icontains=search_query) | 
            Q(state__icontains=search_query) |
            Q(documents__title__icontains=search_query) |
            Q(documents__file__icontains=search_query)
        ).distinct() 

        # Pagination
        paginator = PageNumberPagination()
        paginator.page_size = 10 

        paginated_cases = paginator.paginate_queryset(cases, request)
        serializer = CaseCardSerializer(paginated_cases, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)
        # return Response(serializer.data, status=status.HTTP_200_OK)

   
    def post(self, request):
        serializer = CaseSubmissionSerializer(data=request.data)
        if serializer.is_valid():
            case_instance = serializer.save(user=request.user)

           
            files = request.FILES.getlist('files') 
            for f in files:
                CaseDocument.objects.create(case=case_instance, file=f)
            
            case_instance.press_release_enhanced = request.data.get('press_release', '')
            case_instance.save()
            #link condition add after client metting
            # return Response(CaseSubmissionSerializer(case_instance).data, status=201)
            return Response(CaseSubmissionSerializer(case_instance, context={'request': request}).data, status=201)
        return Response(serializer.errors, status=400)


class CaseDetailAPIView(APIView):
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get_object(self, pk):
        try:
            case = CaseSubmission.objects.get(pk=pk)
            self.check_object_permissions(self.request, case) 
            return case
        except CaseSubmission.DoesNotExist:
            return None

    def get(self, request, pk):
        case = self.get_object(pk)
        if not case:
            return Response({"error": "Case not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = CaseSubmissionSerializer(case)
        return Response(serializer.data)
    
    def put(self, request, pk):
        case = self.get_object(pk)
        if not case:
         return Response({"error": "Case not found"}, status=status.HTTP_404_NOT_FOUND)

    # 1. Normal field gulo update hobe (Title, Number, State etc.)
    
        serializer = CaseSubmissionSerializer(case, data=request.data, partial=True)
    
        if serializer.is_valid():
            serializer.save()
        
        
            new_files = request.FILES.getlist('files') 
            if new_files:
                for f in new_files:
                    CaseDocument.objects.create(case=case, file=f)
        
        # Updated data return korbe (documents list shoho)
            updated_data = CaseSubmissionSerializer(case).data
            return Response(updated_data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

   
    def patch(self, request, pk):
        case = self.get_object(pk)
        if not case:
            return Response({"error": "Case not found"}, status=status.HTTP_404_NOT_FOUND)
        
       
        serializer = CaseSubmissionSerializer(case, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        case = self.get_object(pk)
        if case:
            case.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({"error": "Case not found"}, status=status.HTTP_404_NOT_FOUND)
    
#casse media submission list view (for admin dashboard)
    
class CaseMediaSubmissionListAPIView(APIView):
    permission_classes = [IsAuthenticated]
   
    def get(self, request):
        search_query = request.query_params.get("search", "").strip()
        cases = CaseSubmission.objects.all().order_by('-created_at')

        if search_query:
            cases = cases.filter(
            Q(case_title__icontains=search_query) | 
            Q(case_number__icontains=search_query) | 
            Q(state__icontains=search_query) |
            Q(documents__title__icontains=search_query) |
            Q(documents__file__icontains=search_query)
        ).distinct() 

        # Pagination
        paginator = PageNumberPagination()
        paginator.page_size = 5 

        paginated_cases = paginator.paginate_queryset(cases, request)
        
        serializer = CaseCardMediaSerializer(paginated_cases, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)
    
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class UserCaseStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        stats = CaseSubmission.objects.filter(user=request.user).aggregate(
            total=Count('id'),
            pending=Count('id', filter=Q(case_status='pending')),
            accepted=Count('id', filter=Q(case_status='accepted')),
            rejected=Count('id', filter=Q(case_status='rejected'))
        )
        return Response({"case_stats": "success", "data": stats})
    

#accepted case list view for user dashboard

class AcceptedCaseListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        
        search_query = request.query_params.get("search", "").strip()
        cases = CaseSubmission.objects.filter(
            
            case_status='accepted'
        ).order_by('-created_at')

        
        if search_query:
            cases = cases.filter(
            Q(case_title__icontains=search_query) | 
            Q(case_number__icontains=search_query) | 
            Q(state__icontains=search_query) |
            Q(documents__title__icontains=search_query) |
            Q(documents__file__icontains=search_query)
        ).distinct() 
        paginator = PageNumberPagination()
        paginator.page_size = 10
        paginated_cases = paginator.paginate_queryset(cases, request)
        
        serializer = CaseCardSerializer(paginated_cases, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)
    
   

class AcceptedCaseDetailAPIView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def get_object(self, pk):
        try:
            case = CaseSubmission.objects.get(pk=pk)
            self.check_object_permissions(self.request, case) 
            return case
        except CaseSubmission.DoesNotExist:
            return None

    def get(self, request, pk):
        case = self.get_object(pk)
        if not case:
            return Response({"error": "Case not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = CaseSubmissionSerializer(case)
        return Response(serializer.data)
    
    def put(self, request, pk):
        case = self.get_object(pk)
        if not case:
         return Response({"error": "Case not found"}, status=status.HTTP_404_NOT_FOUND)

    # 1. Normal field gulo update hobe (Title, Number, State etc.)
    
        serializer = CaseSubmissionSerializer(case, data=request.data, partial=True)
    
        if serializer.is_valid():
            serializer.save()
        
        
            new_files = request.FILES.getlist('files') 
            if new_files:
                for f in new_files:
                    CaseDocument.objects.create(case=case, file=f)
        
        # Updated data return korbe (documents list shoho)
            updated_data = CaseSubmissionSerializer(case).data
            return Response(updated_data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

   
    def patch(self, request, pk):
        case = self.get_object(pk)
        if not case:
            return Response({"error": "Case not found"}, status=status.HTTP_404_NOT_FOUND)
        
       
        serializer = CaseSubmissionSerializer(case, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        case = self.get_object(pk)
        if case:
            case.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({"error": "Case not found"}, status=status.HTTP_404_NOT_FOUND)