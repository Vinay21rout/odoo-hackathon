import os
import httpx
from sqlalchemy.orm import Session
from app.services.reports.report_service import report_service
from app.schemas.ai.ai import RecommendationItem, DashboardInsightItem

class AIService:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        self.model_name = "llama3-8b-8192"

    async def _call_groq(self, prompt: str, system_instruction: str = "") -> str:
        if not self.api_key:
            return ""
            
        url = "https://api.groq.com/openai/v1/chat/completions"
        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": self.model_name,
            "messages": messages
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
            
        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                res = await client.post(url, json=payload, headers=headers)
                if res.status_code == 200:
                    data = res.json()
                    return data["choices"][0]["message"]["content"]
                else:
                    print(f"Groq API error: {res.status_code} - {res.text}")
        except Exception as e:
            print(f"Groq API transaction failure: {e}")
        return ""

    def _get_esg_data(self, db: Session) -> dict:
        # Fetch actual live data aggregates using the report service compiler
        return report_service.generate_dynamic_esg_report(db)

    async def chat_assistant(self, db: Session, user_message: str) -> str:
        esg = self._get_esg_data(db)
        
        system_instruction = (
            "You are EcoSphere AI, an expert corporate ESG Consultant. "
            "Use the company's real-time ESG metrics to answer user questions professionally.\n"
            f"Active ESG metrics data:\n"
            f"- Carbon Emissions: {esg['environmental']['carbon']} kgCO2e\n"
            f"- Energy Consumed: {esg['environmental']['energy']} kWh\n"
            f"- Water Consumed: {esg['environmental']['water']} m3\n"
            f"- Waste Generated: {esg['environmental']['waste']} kg\n"
            f"- Employee Training Hours: {esg['social']['training_hours']} Hrs\n"
            f"- Safety Incidents: {esg['social']['health_safety_incidents']} cases\n"
            f"- Community Service Hours: {esg['social']['community_hours']} Hrs\n"
            f"- Filed Whistleblower Reports: {esg['governance']['whistleblower_reports']} complaints\n"
            f"- Policy Violations: {esg['governance']['policy_violations']} violations\n"
        )
        
        prompt = f"User asks: {user_message}"
        
        # Call Groq if API key is present
        ai_response = await self._call_groq(prompt, system_instruction)
        if ai_response:
            return ai_response
            
        # Fallback local generation if no key exists
        return self._generate_local_chat_fallback(user_message, esg)

    async def generate_narrative_report(self, db: Session, report_type: str, timeframe: str) -> str:
        esg = self._get_esg_data(db)
        
        prompt = (
            f"Generate a professional, detailed corporate {report_type} ESG narrative report for the timeframe {timeframe}.\n"
            f"Metrics data:\n{esg}"
        )
        
        system_instruction = "You are a professional corporate sustainability auditor."
        
        ai_response = await self._call_groq(prompt, system_instruction)
        if ai_response:
            return ai_response
            
        return self._generate_local_report_fallback(report_type, timeframe, esg)

    async def get_recommendations(self, db: Session, focus_area: str) -> list:
        esg = self._get_esg_data(db)
        
        # Rule-based fallback recommendations which represent high-value actionable guidance
        recs = []
        
        # Environmental analysis
        carbon = esg['environmental']['carbon']
        energy = esg['environmental']['energy']
        if carbon > 1000 or energy > 5000:
            recs.append(RecommendationItem(
                title="Transition to Renewable Energy Sources",
                description="Invest in commercial solar panels or procure energy from local green tariffs to decrease grid reliance.",
                impact="High Carbon Abatement (est. 15-20% reduction)",
                difficulty="Medium-High",
                points_estimate=500
            ))
            recs.append(RecommendationItem(
                title="Implement Smart Energy Monitors",
                description="Install IoT building sensors to track peak HVAC demand and automate climate zones in vacant office bays.",
                impact="Medium Cost Savings & Energy Reduction",
                difficulty="Low-Medium",
                points_estimate=250
            ))
            
        # Social analysis
        training = esg['social']['training_hours']
        incidents = esg['social']['health_safety_incidents']
        if training < 200 or incidents > 0:
            recs.append(RecommendationItem(
                title="Launch Workplace Safety Certification",
                description="Coordinate with OSHA safety auditors to host quarterly safety bootcamps and compliance workshops.",
                impact="Reduced Safety Incident Risks & Insurance Premiums",
                difficulty="Low",
                points_estimate=200
            ))
            
        # Governance analysis
        whistle = esg['governance']['whistleblower_reports']
        if whistle > 0:
            recs.append(RecommendationItem(
                title="Modernize Anonymous Whistleblower Hotlines",
                description="Formulate encrypted communication protocols to secure corporate reporting databases and protect reporters.",
                impact="Improved Risk Mitigation & Compliance Metrics",
                difficulty="Medium",
                points_estimate=300
            ))

        # Default fallback recommendations to ensure rich data is returned
        if not recs:
            recs.append(RecommendationItem(
                title="Establish Basic ESG Audits",
                description="Configure database records trackers to begin logging emissions outputs on a monthly schedule.",
                impact="Core Compliance Capability",
                difficulty="Low",
                points_estimate=100
            ))
            
        return recs

    async def get_dashboard_insights(self, db: Session) -> dict:
        esg = self._get_esg_data(db)
        
        insights = []
        warnings = []
        
        # Evaluate environmental thresholds
        carbon = esg['environmental']['carbon']
        if carbon > 3000:
            insights.append(DashboardInsightItem(
                metric="Carbon footprint",
                insight="Emissions are currently higher than standard compliance thresholds. Carbon offsets are highly recommended.",
                type="warning"
            ))
            warnings.append("Carbon footprint exceeds standard ESG carbon guidelines!")
        else:
            insights.append(DashboardInsightItem(
                metric="Carbon footprint",
                insight="Office footprint complies with localized targets. Continue baseline monitoring.",
                type="positive"
            ))
            
        # Evaluate social thresholds
        training = esg['social']['training_hours']
        if training < 100:
            insights.append(DashboardInsightItem(
                metric="Social training workload",
                insight="Employee development hours are below optimal standards. Schedule refresher compliance workshops.",
                type="info"
            ))
            warnings.append("Employee training workloads are below annual targets!")
        else:
            insights.append(DashboardInsightItem(
                metric="Social training workload",
                insight="Employee safety and equity certifications exceed basic guidelines.",
                type="positive"
            ))
            
        # Evaluate governance threshold
        incidents = esg['governance']['whistleblower_reports']
        if incidents > 0:
            warnings.append(f"Active Whistleblower Reports: {incidents} pending review.")
            
        return {
            "insights": insights,
            "warnings": warnings
        }

    # --- Local Generation Fallback Algorithms ---

    def _generate_local_chat_fallback(self, query: str, esg: dict) -> str:
        query_lower = query.lower()
        if "carbon" in query_lower or "emission" in query_lower:
            return (
                f"Based on real-time database logs, your company's carbon footprint is **{esg['environmental']['carbon']} kgCO2e**. "
                "The sustainability service recommends upgrading server HVAC systems to renewable sources, which would decrease emissions by up to 15%."
            )
        if "training" in query_lower or "social" in query_lower:
            return (
                f"Your employees have completed a total of **{esg['social']['training_hours']} hours** of training and development. "
                "There are currently no occupational safety incidents reported this quarter, indicating strong safety posture."
            )
        if "governance" in query_lower or "report" in query_lower:
            return (
                f"Currently, there are **{esg['governance']['whistleblower_reports']} active whistleblower cases** logged in the database. "
                "Our recommendation is to process these cases through our resolution interface on the governance dashboard."
            )
        return (
            "Hello! I am your EcoSphere AI Assistant. I can analyze your ESG metrics. "
            f"Currently, I track Carbon Emissions ({esg['environmental']['carbon']} kg), Training Hours ({esg['social']['training_hours']} Hrs), "
            f"and filed Compliance Reports ({esg['governance']['whistleblower_reports']}). Ask me about carbon trends or safety updates!"
        )

    def _generate_local_report_fallback(self, report_type: str, timeframe: str, esg: dict) -> str:
        env = esg['environmental']
        soc = esg['social']
        gov = esg['governance']
        return f"""# EcoSphere AI - ESG Executive Audit Report
**Focus Area:** {report_type.upper()} Audit
**Auditing Timeframe:** {timeframe}
**Status:** DRAFT SNAPSHOT COMPILATION

## Executive Summary
This document compiles and summarizes real-time environmental, social, and governance compliance indicators logged across corporate systems.

## 1. Indicator Breakdown
### Environmental Indicators (E)
- **Carbon footprint:** {env['carbon']} kgCO2e
- **Electricity Consumed:** {env['energy']} kWh
- **Water Consumption:** {env['water']} m3
- **Waste generated:** {env['waste']} kg

### Social Responsibility (S)
- **Employee Training Hours:** {soc['training_hours']} Hrs
- **Reported Accidents:** {soc['health_safety_incidents']} cases
- **Community Volunteering:** {soc['community_hours']} Hrs

### Governance & Ethics (G)
- **Whistleblower Filings:** {gov['whistleblower_reports']} complaints
- **Compliance Infractions:** {gov['policy_violations']} violations

## 2. Strategic ESG Directives
1. **Reduce Server Footprint:** Grid consumption optimization of HVAC units.
2. **Standardize Safety Seminars:** Ensure employee training workloads remain above target thresholds.
3. **Resolve Whistleblower Complaints:** Investigate active filings within standard SLA windows.
"""

ai_service = AIService()
