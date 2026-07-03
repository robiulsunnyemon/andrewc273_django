# Generated manually to populate FAQ data

from django.db import migrations

def populate_faqs(apps, schema_editor):
    FAQ = apps.get_model('cms', 'FAQ')
    
    faqs_data = [
        {
            "order": 1,
            "question": "What is D.O.J.A.?",
            "answer": "D.O.J.A. (Division of Justice in America) is an independent public relations and publishing platform. We allow verified users to share their personal accounts, documents, and statements related to criminal proceedings. Please note, we are not a court, law enforcement agency, or government organization."
        },
        {
            "order": 2,
            "question": "Is D.O.J.A. affiliated with the government?",
            "answer": "No. D.O.J.A. is a private, independent organization and is not affiliated with any court, prosecutor, law enforcement agency, or government office."
        },
        {
            "order": 3,
            "question": "Who can publish on D.O.J.A.?",
            "answer": "Individuals who are currently facing, or have previously faced, criminal prosecution in the United States, as well as their authorized representatives, may apply to publish content. All authors must complete identity verification before publishing."
        },
        {
            "order": 4,
            "question": "Does D.O.J.A. provide legal advice?",
            "answer": "No. D.O.J.A. does not provide legal representation, legal advice, or legal opinions. We strongly encourage all users to consult with licensed attorneys for any legal matters."
        },
        {
            "order": 5,
            "question": "Is the information on D.O.J.A. verified?",
            "answer": "While authors are required to verify their identity, all published content represents the views and claims of the individual authors. D.O.J.A. does not independently verify every factual allegation made in a submission."
        },
        {
            "order": 6,
            "question": "Can I remove my content later?",
            "answer": "Yes. Authors may request removal or modification of their published materials, subject to our archival and legal policies. Please be aware that some records may remain archived for transparency purposes, even if removed from the public view."
        },
        {
            "order": 7,
            "question": "Can publishing on D.O.J.A. affect my legal case?",
            "answer": "Yes, publishing information may have legal consequences. D.O.J.A. strongly recommends consulting with your attorney before drafting or submitting any content. We are not responsible for how published material may be used by others."
        },
        {
            "order": 8,
            "question": "Is D.O.J.A. a news organization?",
            "answer": "D.O.J.A. operates as a publishing and public relations platform. We host user-submitted press releases and materials, but we are not a traditional newsroom with editorial oversight of factual content."
        },
        {
            "order": 9,
            "question": "Can journalists use D.O.J.A. materials?",
            "answer": "Yes. Journalists and researchers may reference publicly available materials on our site, subject to proper attribution and applicable laws."
        },
        {
            "order": 10,
            "question": "Does D.O.J.A. censor content?",
            "answer": "D.O.J.A. does not censor viewpoints. However, we reserve the right to decline or remove content that violates our Terms of Service, defamation laws, privacy laws, state or federal laws, or our safety policies."
        },
        {
            "order": 11,
            "question": "Can anonymous posts be published?",
            "answer": "Generally, no. Authors must be verified to ensure accountability. Limited exceptions may apply under special circumstances for stories submitted behind the Wall."
        },
        {
            "order": 12,
            "question": "Does D.O.J.A. edit submissions?",
            "answer": "We may make minor formatting and clarity edits (potentially with the help of AI) if an author requests assistance. All substantive content remains the sole responsibility of the author."
        },
        {
            "order": 13,
            "question": "How much does it cost to use D.O.J.A.?",
            "answer": "Basic publishing services are currently offered at no cost. We may introduce optional premium services in future phases."
        },
        {
            "order": 14,
            "question": "How are stories selected for the podcast or media projects?",
            "answer": "Stories are reviewed based on public interest, documentation quality, legal considerations, and production feasibility. Please note that selection is entirely discretionary."
        },
        {
            "order": 15,
            "question": "Does D.O.J.A. guarantee media coverage?",
            "answer": "No. Submitting your story does not guarantee press coverage, a podcast appearance, or any production deals."
        },
        {
            "order": 16,
            "question": "What happens if false information is submitted?",
            "answer": "Submitting false or misleading information may result in the removal of content, account suspension, and potential legal consequences. Users are solely responsible for the accuracy of their submissions."
        },
        {
            "order": 17,
            "question": "How is user privacy protected?",
            "answer": "Personal information is protected in accordance with privacy laws and our privacy policy. Only the information necessary for your publication is displayed publicly."
        },
        {
            "order": 18,
            "question": "How can I contact D.O.J.A.?",
            "answer": "You can reach us through our Contact page for general inquiries, media requests, legal notices, or technical support."
        }
    ]

    for faq in faqs_data:
        FAQ.objects.update_or_create(
            order=faq["order"],
            defaults={
                "question": faq["question"],
                "answer": faq["answer"],
                "is_active": True
            }
        )

def remove_faqs(apps, schema_editor):
    FAQ = apps.get_model('cms', 'FAQ')
    FAQ.objects.filter(order__gte=1, order__lte=18).delete()

class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0003_alter_faq_order'),
    ]

    operations = [
        migrations.RunPython(populate_faqs, remove_faqs),
    ]
