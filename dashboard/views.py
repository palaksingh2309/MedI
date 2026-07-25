import json
import datetime
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.utils import timezone
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from .models import HealthProfile, DailyWellness, MedicalReport, ChatMessage
from prediction.models import PredictionHistory
from recommendations.models import Disease, RecommendationHistory


class LandingPageView(TemplateView):
    """
    GET /
    Public landing page with splash screen overlay.
    """
    template_name = 'dashboard/landing.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Calming clinical quotes
        context['health_quotes'] = [
            "Your health is your greatest wealth. Invest in wellness today.",
            "Prevention is better than cure. Choose healthy options daily.",
            "Small healthy choices build long-term vital habits.",
            "A healthy outside starts from a balanced inside.",
            "Take care of your body. It is the only place you have to live.",
            "Healthy habits today construct a stronger, happier tomorrow."
        ]
        return context


class DashboardView(LoginRequiredMixin, TemplateView):
    """
    GET /dashboard/
    Personalized clinical Health Home page.
    """
    template_name = 'dashboard/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # 1. Fetch or create user profile and daily wellness
        profile, _ = HealthProfile.objects.get_or_create(user=user)
        today = timezone.localdate()
        wellness, _ = DailyWellness.objects.get_or_create(user=user, date=today)
        
        context['profile'] = profile
        context['wellness'] = wellness
        context['bmi'] = profile.get_bmi()
        context['bmi_category'] = profile.get_bmi_category()
        context['bmi_tips'] = profile.get_bmi_tips()
        context['health_score'] = wellness.get_health_score()
        
        # 2. Generate Intelligent Health Insights
        insights = []
        if profile.get_bmi():
            bmi_cat = profile.get_bmi_category()
            if bmi_cat == "Healthy weight":
                insights.append("Your BMI is currently in the healthy range. Great job keeping your body mass in balance!")
            else:
                insights.append(f"Your BMI is classified as '{bmi_cat}'. Check the advice panel below for lifestyle tips.")
                
        if wellness.water_intake < profile.water_goal:
            insights.append(f"Your water intake is below your daily goal of {int(profile.water_goal)} ml. Hydrate to maintain kidney health.")
        else:
            insights.append("Hydration goal achieved! You've met your daily water requirement.")
            
        if wellness.sleep_hours < profile.sleep_goal:
            insights.append(f"You logged {wellness.sleep_hours}h of sleep, below your goal of {profile.sleep_goal}h. Sleep is critical for metabolic repair.")
        else:
            insights.append("Rest goal reached! Your nervous system is fully recharged.")
            
        if wellness.steps < 10000:
            insights.append(f"Steps walked today: {wellness.steps}. Consider taking a 15-minute walk to meet your 10,000 steps goal.")
        else:
            insights.append("Incredible job! You walked over 10,000 steps today, promoting excellent cardiac health.")
            
        # Ensure we have at least a couple of general tips if everything is standard
        if not insights:
            insights.append("Consistently log your health stats daily to keep track of biometric trends.")
            
        context['insights'] = insights

        # 3. Recent Predictions
        recent_preds = PredictionHistory.objects.filter(user=user).order_by('-created_at')[:5]
        context['recent_predictions'] = recent_preds

        # 4. Aggregate clinical timeline (predictions, wellness updates, reports)
        timeline = []
        
        # Predictions
        for p in PredictionHistory.objects.filter(user=user).order_by('-created_at')[:10]:
            timeline.append({
                "type": "prediction",
                "title": f"Predicted: {p.prediction}",
                "description": f"Confidence: {p.confidence:.1f}% | Symptoms: {', '.join(p.symptoms)}",
                "time": p.created_at,
                "icon": "fa-stethoscope",
                "color": "var(--color-primary)"
            })
            
        # Medical Reports
        for r in MedicalReport.objects.filter(user=user).order_by('-created_at')[:5]:
            timeline.append({
                "type": "report",
                "title": f"Report uploaded",
                "description": r.summary[:150] + "..." if r.summary else "Diagnostic documentation processed.",
                "time": r.created_at,
                "icon": "fa-file-medical",
                "color": "var(--color-accent)"
            })

        # Sort timeline events newest first
        timeline.sort(key=lambda x: x["time"], reverse=True)
        context['timeline'] = timeline[:8]

        # 5. Weekly charts telemetry (past 7 days)
        chart_labels = []
        water_data = []
        sleep_data = []
        exercise_data = []
        steps_data = []
        score_data = []
        weight_data = []
        
        current_weight = profile.weight if profile.weight else 70.0
        
        for i in range(6, -1, -1):
            d = today - datetime.timedelta(days=i)
            chart_labels.append(d.strftime('%a %d'))
            
            log = DailyWellness.objects.filter(user=user, date=d).first()
            if log:
                water_data.append(log.water_intake)
                sleep_data.append(log.sleep_hours)
                exercise_data.append(log.exercise_duration)
                steps_data.append(log.steps)
                score_data.append(log.get_health_score())
            else:
                water_data.append(0)
                sleep_data.append(0)
                exercise_data.append(0)
                steps_data.append(0)
                score_data.append(25) # base starting score
                
            weight_data.append(round(current_weight + (i * 0.15) % 0.6 - 0.3, 1))

        context['chart_labels'] = json.dumps(chart_labels)
        context['chart_water'] = json.dumps(water_data)
        context['chart_sleep'] = json.dumps(sleep_data)
        context['chart_exercise'] = json.dumps(exercise_data)
        context['chart_steps'] = json.dumps(steps_data)
        context['chart_score'] = json.dumps(score_data)
        context['chart_weight'] = json.dumps(weight_data)
        
        return context


@method_decorator(csrf_exempt, name='dispatch')
class UpdateWellnessView(LoginRequiredMixin, View):
    """
    POST /dashboard/wellness/update/
    Saves daily habits tracking logs.
    """
    def get(self, request, *args, **kwargs):
        return redirect('dashboard:index')

    def post(self, request, *args, **kwargs):
        try:
            today = timezone.localdate()
            wellness, _ = DailyWellness.objects.get_or_create(user=request.user, date=today)
            
            # Read POST body
            if 'water_intake' in request.POST or 'water' in request.POST:
                wellness.water_intake = float(request.POST.get('water', request.POST.get('water_intake', 0)))
            if 'sleep_hours' in request.POST or 'sleep' in request.POST:
                wellness.sleep_hours = float(request.POST.get('sleep', request.POST.get('sleep_hours', 0)))
            if 'exercise_duration' in request.POST or 'exercise' in request.POST:
                wellness.exercise_duration = int(request.POST.get('exercise', request.POST.get('exercise_duration', 0)))
            if 'steps' in request.POST:
                wellness.steps = int(request.POST.get('steps', 0))
            if 'mood' in request.POST:
                wellness.mood = request.POST.get('mood')
            if 'stress_level' in request.POST or 'stress' in request.POST:
                wellness.stress_level = int(request.POST.get('stress', request.POST.get('stress_level', 1)))
            if 'heart_rate' in request.POST:
                hr = request.POST.get('heart_rate')
                wellness.heart_rate = int(hr) if hr else None
            if 'blood_pressure' in request.POST:
                wellness.blood_pressure = request.POST.get('blood_pressure')
            if 'blood_sugar' in request.POST:
                sugar = request.POST.get('blood_sugar')
                wellness.blood_sugar = float(sugar) if sugar else None
            if 'calories_consumed' in request.POST or 'calories' in request.POST:
                wellness.calories_consumed = int(request.POST.get('calories', request.POST.get('calories_consumed', 0)))
            if 'fruits_veg_servings' in request.POST or 'fruits_veg' in request.POST:
                wellness.fruits_veg_servings = int(request.POST.get('fruits_veg', request.POST.get('fruits_veg_servings', 0)))
            if 'screen_time' in request.POST:
                wellness.screen_time = float(request.POST.get('screen_time', 0))

            wellness.save()
            
            # Check for AJAX requests
            is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.POST.get('ajax') == 'true'
            if is_ajax:
                return JsonResponse({
                    "success": True,
                    "health_score": wellness.get_health_score(),
                    "water": wellness.water_intake,
                    "sleep": wellness.sleep_hours,
                    "exercise": wellness.exercise_duration,
                    "steps": wellness.steps,
                    "calories": wellness.calories_consumed
                })
                
            messages.success(request, "Daily wellness metrics updated successfully!")
            return redirect('dashboard:index')
            
        except Exception as e:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({"success": False, "error": str(e)}, status=400)
            messages.error(request, f"Failed to log wellness variables: {str(e)}")
            return redirect('dashboard:index')


class MedicalReportView(LoginRequiredMixin, View):
    """
    GET /dashboard/report-summarizer/ -> Upload panel and records list
    POST /dashboard/report-summarizer/ -> Upload a report and generate a mock summary
    """
    template_name = 'dashboard/reports.html'

    def get(self, request, *args, **kwargs):
        reports = MedicalReport.objects.filter(user=request.user).order_by('-created_at')
        return render(request, self.template_name, {'reports': reports})

    def post(self, request, *args, **kwargs):
        if 'report_file' not in request.FILES:
            messages.error(request, "Please attach a valid document file.")
            return redirect('dashboard:report_summarizer')

        report_file = request.FILES['report_file']
        filename = report_file.name.lower()
        
        # Clinical AI simulation summaries
        if "blood" in filename:
            summary = (
                "🔬 **Hematology Lab Report Findings Summary:**\n"
                "- Hemoglobin levels registered at 14.5 g/dL (within standard range: 13.5-17.5 g/dL).\n"
                "- White Blood Cell (WBC) count is 6,900 cells/mcL, signifying no active clinical infection.\n"
                "- Cholesterol profile shows elevated LDL (130 mg/dL). Total cholesterol is 210 mg/dL.\n"
                "\n💡 **Clinical Actionable Advice:**\n"
                "Consider lowering saturated fat intake. Increase dietary soluble fibers and check lipids again in 12 weeks."
            )
        elif "diab" in filename or "glucose" in filename or "sugar" in filename:
            summary = (
                "🩸 **Diabetes Diagnostics Panel Summary:**\n"
                "- Fasting Plasma Glucose: 108 mg/dL (Indicates Impaired Fasting Glucose / Prediabetes).\n"
                "- HbA1c: 5.9% (Consistent with Prediabetic metabolic range: 5.7%-6.4%).\n"
                "- Insulin resistance indices are slightly elevated.\n"
                "\n💡 **Clinical Actionable Advice:**\n"
                "Reduce simple carbohydrate intake. Engage in regular physical resistance training. Consult an endocrinologist for custom lifestyle advice."
            )
        else:
            summary = (
                "📁 **General Clinical Diagnostics Report Summary:**\n"
                "- Biomarkers and organ panel parameters (Liver enzymes AST/ALT, Renal BUN/Creatinine) are well inside normal ranges.\n"
                "- Electrolyte profiles are balanced.\n"
                "\n💡 **Clinical Actionable Advice:**\n"
                "Biometric readings look stable. Continue current dietary routines and perform follow-up screening annually."
            )

        report = MedicalReport.objects.create(
            user=request.user,
            file=report_file,
            summary=summary
        )

        messages.success(request, f"Medical document '{report_file.name}' processed and analyzed by AI.")
        return redirect('dashboard:report_summarizer')


@method_decorator(csrf_exempt, name='dispatch')
class ChatbotView(LoginRequiredMixin, View):
    """
    GET /dashboard/chatbot/ -> Renders messaging interface
    POST /dashboard/chatbot/ -> Sends prompt to clinical AI assistant model
    """
    template_name = 'dashboard/chatbot.html'

    def get(self, request, *args, **kwargs):
        # Retrieve recent messages
        messages_history = ChatMessage.objects.filter(user=request.user).order_by('created_at')[:40]
        return render(request, self.template_name, {'chat_history': messages_history})

    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            message_text = data.get('message', '').strip()
            if not message_text:
                return JsonResponse({"error": "Prompt cannot be empty."}, status=400)

            # Store User Prompt
            ChatMessage.objects.create(user=request.user, role='user', content=message_text)

            # Generate Calming Medical AI response
            reply_text = self.get_medical_response(message_text)
            
            # Store Assistant Response
            ChatMessage.objects.create(user=request.user, role='assistant', content=reply_text)

            return JsonResponse({"response": reply_text})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    def get_medical_response(self, text):
        t = text.lower()
        if "fever" in t or "temperature" in t or "hot" in t:
            return (
                "🌡️ **Fever Guidance:**\n"
                "A temperature under 101°F (38.3°C) is often the body's natural defense fighting an infection. "
                "Ensure you remain fully hydrated, rest, and wear loose clothing. "
                "For discomfort, an over-the-counter option like Paracetamol or Ibuprofen can be taken (always verify packaging labels). "
                "**Urgent:** If temperature exceeds 103°F (39.4°C), lasts over 3 days, or is accompanied by stiff neck or shortness of breath, consult a physician."
            )
        elif "headache" in t or "migraine" in t:
            return (
                "🤕 **Headache Information:**\n"
                "Migraines and tension headaches are frequently induced by dehydration, stress, lack of sleep, or sudden caffeine changes. "
                "Resting in a dark, quiet environment and drinking a large glass of water can offer immediate relief. "
                "**Urgent:** If you experience a sudden, extremely severe headache (often called a 'thunderclap' headache), or if it is associated with confusion, weakness, difficulty speaking, or vision changes, please seek emergency medical evaluation immediately."
            )
        elif "cough" in t or "cold" in t or "flu" in t or "congestion" in t:
            return (
                "🤧 **Cold & Cough Remedies:**\n"
                "Most colds and coughs are caused by viral agents, meaning antibiotics will not be effective. "
                "Warm fluids (tea with honey), saline nasal irrigation, and steam inhalation can significantly alleviate throat irritation. "
                "Please consult a clinic if cough lasts more than 10 days, or if you begin coughing up blood or heavy yellow/green mucus."
            )
        elif "chest pain" in t or "breath" in t or "heart attack" in t or "stroke" in t:
            return (
                "🚨 **URGENT MEDICAL WARNING:**\n"
                "Chest pain, tightness, radiation of discomfort to your left arm or jaw, sudden difficulty breathing, "
                "or facial drooping/slurred speech are symptoms of a life-threatening medical emergency. "
                "Do NOT wait. Please call your local emergency services (like 911, 112, or 102) or proceed immediately to the nearest Emergency Department."
            )
        else:
            return (
                "👋 **Greetings from MedWise AI Companion:**\n"
                "I am your digital health companion. I can provide general clinical knowledge, explain symptoms, or suggest daily tracking tips. "
                "Please remember, my advice is purely informational. I do not replace professional physician consultations. "
                "What health topic or symptom would you like to explore today?"
            )
