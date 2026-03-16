import base64
#import openai
from django.conf import settings

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import CaseSubmission, CaseDocument
from .serializers import CaseSubmissionSerializer, CaseDocumentSerializer

#client = openai.OpenAI(api_key=settings.OPEN_AI_API_KEY)

def enhance_case_text(user_text):
    """
    AI Analysis using OpenAI GPT-4o with Retry Logic (Similar to your dental app)
    """
    max_retries = 3
    
    
    PROMPT = """
    Analyze the provided legal case text and enhance it.
    CRITICAL GUIDELINES:
    1. PROFESSIONALISM: Use formal legal language.
    2. STRUCTURE: Organize into clear paragraphs (Background, Facts, Request).
    3. DISCLAIMER: Subtly mention that this is an AI-enhanced draft and requires legal review.
    4. FORMAT: Respond ONLY in JSON format.
    
    Example JSON structure:
    {
        "status": "success",
        "enhanced_text": "Your professional text here...",
        "summary": "Short summary of changes"
    }
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
    OpenAI GPT-4o ব্যবহার করে লিঙ্ক থেকে তথ্য সংগ্রহ ও সামারি করা (Retry Logic সহ)
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
    def get (self, request):
        return Response({"message": "Send a POST request with 'text' to enhance."},status=status.HTTP_200_OK)
    
    def post(self, request):
        user_text = request.data.get('text', '')
        
        if not user_text:
            return Response({"error": "No text provided"}, status=status.HTTP_400_BAD_REQUEST)

       
        ai_response = enhance_case_text(user_text)

        if ai_response.get('status') == 'failed':
            return Response(ai_response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
        





class CaseSubmissionListCreateAPIView(APIView):
   
    def get(self, request):
        cases = CaseSubmission.objects.all().order_by('-created_at')
        serializer = CaseSubmissionSerializer(cases, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

   
    def post(self, request):
        
        serializer = CaseSubmissionSerializer(data=request.data)
        
        if serializer.is_valid():
          
            case_instance = serializer.save()
            
          
            files = request.FILES.getlist('files') 
            for f in files:
                CaseDocument.objects.create(case=case_instance, file=f)
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CaseDetailAPIView(APIView):
    def get_object(self, pk):
        try:
            return CaseSubmission.objects.get(pk=pk)
        except CaseSubmission.DoesNotExist:
            return None

    def get(self, request, pk):
        case = self.get_object(pk)
        if not case:
            return Response({"error": "Case not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = CaseSubmissionSerializer(case)
        return Response(serializer.data)

    def delete(self, request, pk):
        case = self.get_object(pk)
        if case:
            case.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({"error": "Case not found"}, status=status.HTTP_404_NOT_FOUND)