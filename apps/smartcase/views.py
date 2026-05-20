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
from apps.resources.utils import PrisonPagination
from apps.smartcase.permissions import IsOwnerOrReadOnly

from .models import CaseSubmission, CaseDocument, LegalArgument, Story, PodcastStory
from .serializers import CaseCardMediaSerializer, CaseCardSerializer, CaseSubmissionSerializer, CaseDocumentSerializer, PodcastStorySerializer, PublicProfileSerializer, StorySerializer
from django.db.models import Q, Count
from rest_framework.pagination import PageNumberPagination
from .throttles import AIUsageThrottle
from apps.users.models import Profile, SocialLink 
from rest_framework.parsers import MultiPartParser, FormParser




from django.contrib.auth import get_user_model
User = get_user_model()


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
    permission_classes = [IsAuthenticated]
    throttle_classes = [AIUsageThrottle]
    
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
    permission_classes = [IsAuthenticated]
    throttle_classes = [AIUsageThrottle]
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
        state_filter = request.query_params.get("state", "").strip()
        status_filter = request.query_params.get("status", "all").strip().lower()
        #cases = CaseSubmission.objects.all().order_by('-created_at')
        cases = CaseSubmission.objects.filter(user=request.user).order_by('-created_at')
        if status_filter != 'all':
            if status_filter == 'published':
             cases = cases.filter(case_status='accepted') # 
            elif status_filter in ['pending', 'rejected']:
             cases = cases.filter(case_status=status_filter)

        if state_filter:
            cases = cases.filter(state__iexact=state_filter)
        

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

   
    # def post(self, request):
    #     # serializer = CaseSubmissionSerializer(data=request.data)
    #     serializer = CaseSubmissionSerializer(data=request.data, context={'request': request})
        
    #     if serializer.is_valid():
    #         case_instance = serializer.save(user=request.user)

           
    #         files = request.FILES.getlist('files') 
    #         for f in files:
    #             CaseDocument.objects.create(case=case_instance, file=f)
            
    #         case_instance.press_release_enhanced = request.data.get('press_release', '')
    #         case_instance.save()
    #         #link condition add after client metting
    #         # return Response(CaseSubmissionSerializer(case_instance).data, status=201)
    #         return Response(CaseSubmissionSerializer(case_instance, context={'request': request}).data, status=201)
    #     return Response(serializer.errors, status=400)
    

  
    def post(self, request):
        serializer = CaseSubmissionSerializer(data=request.data,context={'request': request})

        if serializer.is_valid():
            try:
                case_instance = serializer.save(user=request.user)

                files = request.FILES.getlist('files')

                for f in files:
                    if f.size > 50 * 1024 * 1024:
                        return Response(
                            {
                                "message": "File size must be less than 50MB"
                            },
                            status=400
                        )

                    CaseDocument.objects.create(case=case_instance,file=f)

                case_instance.press_release_enhanced = request.data.get('press_release', '')

                case_instance.save()

                return Response(
                {"message": "Case submitted successfully","data": CaseSubmissionSerializer(case_instance,context={'request': request}).data},status=201)

            except Exception:
                return Response(
                {
                    "message": "File size must be less than 50MB"
                },
                status=400
            )

    # return Response(serializer.errors, status=400)

    
    # def post(self, request):
    #     # 1. Serializer initialize kora
    #     serializer = CaseSubmissionSerializer(data=request.data, context={'request': request})
        
    #     if serializer.is_valid():
    #         # 2. Case create kora (user assign shoho)
    #         case_instance = serializer.save(user=request.user)

    #         # 3. File upload handle kora (Multiple files)
    #         files = request.FILES.getlist('files') 
    #         for f in files:
    #             CaseDocument.objects.create(case=case_instance, file=f)
            
    #         # 4. Legal Arguments handle kora (Jodi user pathay)
    #         # Frontend theke 'arguments' namer key-te data thakte hobe
    #         arguments_data = request.data.get('arguments')
    #         if arguments_data:
    #             import json
    #             try:
    #                 # Form-data-te thakle json loads lagte pare
    #                 if isinstance(arguments_data, str):
    #                     arguments_data = json.loads(arguments_data)
                    
    #                 for arg in arguments_data:
    #                     LegalArgument.objects.create(
    #                         case=case_instance,
    #                         title=arg.get('title'),
    #                         content=arg.get('content')
    #                     )
    #             except Exception as e:
    #                 print(f"Error parsing arguments: {e}")

    #         # 5. Press Release Enhanced & AI Summary manually update
    #         # User press_release pathale ota enhanced field-e save hobe
    #         case_instance.press_release_enhanced = request.data.get('press_release', case_instance.press_release)
            
    #         # AI summary field-tio update kora holo (jodi pathay)
    #         case_instance.ai_analysis_summary = request.data.get('ai_analysis_summary', '')
            
    #         case_instance.save()
            
    #         # 6. Response return
    #         return Response(
    #             CaseSubmissionSerializer(case_instance, context={'request': request}).data, 
    #             status=status.HTTP_201_CREATED
    #         )
            
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
    
    # def put(self, request, pk):
    #     case = self.get_object(pk)
    #     if not case:
    #      return Response({"error": "Case not found"}, status=status.HTTP_404_NOT_FOUND)

    # # 1. Normal field gulo update hobe (Title, Number, State etc.)
    
    #     serializer = CaseSubmissionSerializer(case, data=request.data, partial=True,)
    
    #     if serializer.is_valid():
    #         serializer.save()
        
        
    #         new_files = request.FILES.getlist('files') 
    #         if new_files:
    #             for f in new_files:
    #                 CaseDocument.objects.create(case=case, file=f)
        
    #     # Updated data return korbe (documents list shoho)
    #         updated_data = CaseSubmissionSerializer(case).data
    #         return Response(updated_data)

    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def put(self, request, pk):
        case = self.get_object(pk)
        if not case:
         return Response({"error": "Case not found"}, status=status.HTTP_404_NOT_FOUND)

    # primary fields update hobe (Title, Number, State etc.)
        serializer = CaseSubmissionSerializer(case, data=request.data, partial=True, context={'request': request})
    
        if serializer.is_valid():

          serializer.save()
          new_files = request.FILES.getlist('files') 
          if new_files:
              for f in new_files:
                  CaseDocument.objects.create(case=case, file=f)

        
          updated_data = CaseSubmissionSerializer(case, context={'request': request}).data
        # Return updated data (including documents list)
          return Response(updated_data, status=status.HTTP_200_OK)

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
            return Response({"message": "Case deleted successfully"}, status=status.HTTP_200_OK)
        return Response({"error": "Case not found"}, status=status.HTTP_404_NOT_FOUND)
    
#casse media submission list view (for admin dashboard)
    
class CaseMediaSubmissionListAPIView(APIView):
    permission_classes = [AllowAny]
   
    def get(self, request):
        media_type = request.query_params.get("media_type", "all").strip() # mp4 or others
        search_query = request.query_params.get("search", "").strip()
        state_filter = request.query_params.get("state", "").strip()
        cases = CaseSubmission.objects.all().order_by('-created_at')
        # cases = CaseSubmission.objects.filter(case_status="accepted").order_by('-created_at')
        # cases = CaseSubmission.objects.filter(case_status="accepted",documents__document_type__iexact="mp4").distinct().order_by('-created_at')
        
            
        if state_filter:
            cases = cases.filter(state__iexact=state_filter)

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
    
        # return Response(serializer.data, status=status.HTTP_200_OK)
    

class UserCaseStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        stats = CaseSubmission.objects.filter(user=request.user).aggregate(
            total=Count('id',distinct=True),
            # total_podcast=Count('documents', distinct=True),
            # pending=Count('id', filter=Q(case_status='pending'),distinct=True),
            # accepted=Count('id', filter=Q(case_status='accepted'),distinct=True),
            # rejected=Count('id', filter=Q(case_status='rejected'),distinct=True)
        )
        return Response({"case_stats": "success", "data": stats})
    

#accepted case list view for user dashboard

class AcceptedCaseListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        
        search_query = request.query_params.get("search", "").strip()
        state_filter = request.query_params.get("state", "").strip()

        court_filter = request.query_params.get("court_type", "").strip()
        district_filter = request.query_params.get("federal_district", "").strip()
        verified_filter = request.query_params.get("is_verified", "").strip()
        start_date = request.query_params.get("start_date", "").strip()
        end_date = request.query_params.get("end_date", "").strip()
        ordering = request.query_params.get("ordering", "-created_at")
        
        # cases = CaseSubmission.objects.filter(
            
        #     case_status='accepted'
        # ).order_by('-created_at')
        cases = CaseSubmission.objects.all().order_by('-created_at')


        if state_filter:
            cases = cases.filter(state__iexact=state_filter)
        
        if court_filter:
            cases = cases.filter(court_type__iexact=court_filter)

        if district_filter:
            cases = cases.filter(federal_district__iexact=district_filter)


        # Date range filter
        if start_date and end_date:
            cases = cases.filter(filed_date__range=[start_date, end_date])

        
        if search_query:
            cases = cases.filter(
            Q(case_title__icontains=search_query) | 
            Q(case_number__icontains=search_query) | 
            Q(state__icontains=search_query) |
            Q(documents__title__icontains=search_query) |
            Q(author__icontains=search_query) |
            Q(court_type__icontains=search_query) |
            Q(documents__file__icontains=search_query)
        ).distinct() 
        paginator = PageNumberPagination()
        paginator.page_size = 10
        paginated_cases = paginator.paginate_queryset(cases, request)
        
        serializer = CaseCardSerializer(paginated_cases, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)
    
   
       
   

class AcceptedCaseDetailAPIView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly,IsOwnerOrReadOnly]

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
    
    
# class AuthorProfileView(APIView):
#     permission_classes = [permissions.AllowAny]

#     def get(self, request, user_id=None):
#        
#         user = get_object_or_404(User, id=user_id)
        
#       
#         try:
#             profile = user.profile
#         except Exception:
#             return Response({"error": "Profile not found for this user"}, status=404)
        
#         
#         profile_serializer = PublicProfileSerializer(profile, context={'request': request})
        
#        
#         cases = CaseSubmission.objects.filter(user=user, case_status='accepted').order_by('-created_at')
        
#         # Pagination
#         paginator = PageNumberPagination()
#         paginator.page_size = 5
#         paginated_cases = paginator.paginate_queryset(cases, request)
#         case_serializer = CaseSubmissionSerializer(paginated_cases, many=True, context={'request': request})

#         return Response({
#             "profile": profile_serializer.data,
#             "archive_cases": paginator.get_paginated_response(case_serializer.data).data
#         })
    
class AuthorProfileView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, user_id=None):
        
        user = get_object_or_404(User, id=user_id)
        profile = user.profile
        profile_serializer = PublicProfileSerializer(profile, context={'request': request})
        user_cases = CaseSubmission.objects.filter(user=user, case_status='accepted').order_by('-created_at')
        
        paginator = PageNumberPagination()
        paginator.page_size = 10
        
        paginated_cases = paginator.paginate_queryset(user_cases, request)
        
        archive_data = CaseSubmissionSerializer(paginated_cases, many=True, context={'request': request})
        media_data = CaseCardMediaSerializer(paginated_cases, many=True, context={'request': request})

        return Response({
            "profile": profile_serializer.data,
            "archive": paginator.get_paginated_response(archive_data.data).data,
            "media": paginator.get_paginated_response(media_data.data).data
        })
  





class PublicStatsView(APIView):
    """
    
    Case Documented, Verified Author, Districts Outcomes
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        # Case Documented:
        total_cases = CaseSubmission.objects.filter(case_status='accepted').count()
        
        # Verified Author: mustbe 2 link
        
        verified_authors_count = SocialLink.objects.annotate(
            link_filled_count=(
                Count('facebook', filter=~Q(facebook='')) +
                Count('x', filter=~Q(x='')) +
                Count('instagram', filter=~Q(instagram='')) +
                Count('youtube', filter=~Q(youtube='')) +
                Count('truth', filter=~Q(truth=''))
            )
        ).filter(link_filled_count__gte=2).count()

        # Districts Represented: 
        districts_count = CaseSubmission.objects.filter(
            case_status='accepted'
        ).values('federal_district').distinct().count()

        # Favourable Outcomes:
        favourable_outcomes = total_cases

        return Response({
            "case_documented": f"{total_cases:,}",         
            "verified_author": f"{verified_authors_count:,}", 
            "districts_represented": districts_count,     
            "favourable_outcomes": f"{favourable_outcomes:,}" 
        })
    


class StoryView(APIView):
    permission_classes = [IsOwnerOrReadOnly]
    parser_classes = [MultiPartParser, FormParser]
    

    def get(self, request):

        queryset = Story.objects.all().order_by('-created_at')
        
        search_query = request.query_params.get('search', None)

        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query)
            )
        
        featured = request.query_params.get('featured')

        if featured == 'true':
            queryset = queryset.filter(is_featured=True)

        paginator = PrisonPagination()
        paginated_queryset = paginator.paginate_queryset(queryset, request)
        

        serializer = StorySerializer(
            paginated_queryset,
            many=True,
            context={'request': request}
        )
            
        # serializer = StorySerializer(queryset, many=True,context={'request': request})
        # return Response(serializer.data, status=status.HTTP_200_OK)
        return paginator.get_paginated_response(serializer.data)

    
    def post(self, request):
        serializer = StorySerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response({
                "message": "Story submitted successfully!",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class StoryDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk):
        
        story = get_object_or_404(Story, pk=pk)
        serializer = StorySerializer(story, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
class PodcastStoryView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        queryset = PodcastStory.objects.all().order_by('-created_at')

        search_query = request.query_params.get('search', None)

        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query)
            )

        paginator = PrisonPagination()
        paginated_queryset = paginator.paginate_queryset(queryset, request)

        serializer = PodcastStorySerializer(
            paginated_queryset,
            many=True
        )

        return paginator.get_paginated_response(serializer.data)
        # serializer = PodcastStorySerializer(queryset, many=True)
        # return Response(serializer.data, status=status.HTTP_200_OK)


class PodcastStoryDetailView(APIView):
    # permission_classes = [AllowAny]

    def get(self, request, id):
        
        podcast_story = get_object_or_404(PodcastStory, id=id)
        
        serializer = PodcastStorySerializer(podcast_story, context={'request': request})
        
        return Response(serializer.data, status=status.HTTP_200_OK)