"""
Example Enhanced Workflow

Demonstrates the complete Medical AI Agent workflow with all enhancements:
- Enhanced patient context with demographics and lab results
- Drug interaction checking
- Medication scheduling
- RAG with caching
- WhatsApp notifications

This is a standalone example that can be run to see the system in action.
"""

import asyncio
from datetime import datetime
from medical_ai_agent.models import (
    PatientContext,
    Medicine,
    LabResult,
    ExtractedPrescription,
    ClinicalAssessment
)
from medical_ai_agent.drug_interaction_checker import DrugInteractionChecker
from medical_ai_agent.medication_scheduler import get_schedule_generator
from medical_ai_agent.rag_cache import get_rag_cache


def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


async def example_enhanced_workflow():
    """Demonstrate complete enhanced workflow."""
    
    print_section("MEDICAL AI AGENT - ENHANCED WORKFLOW DEMO")
    
    # ========================================================================
    # Step 1: Create Enhanced Patient Context
    # ========================================================================
    print_section("Step 1: Enhanced Patient Context")
    
    # Define current medications
    current_medications = [
        Medicine(
            name="Metformin",
            strength="500mg",
            frequency="1-0-1",
            instructions="Take with meals",
            duration_days=30,
            started_date="2024-01-01"
        ),
        Medicine(
            name="Amlodipine",
            strength="5mg",
            frequency="1-0-0",
            instructions="Take in morning",
            duration_days=30,
            started_date="2024-01-01"
        )
    ]
    
    # Define lab results
    lab_results = [
        LabResult(
            test_name="Serum Creatinine",
            value="1.8",
            unit="mg/dL",
            reference_range="0.7-1.3",
            date="2024-01-15",
            is_abnormal=True
        ),
        LabResult(
            test_name="HbA1c",
            value="7.8",
            unit="%",
            reference_range="<5.7",
            date="2024-01-15",
            is_abnormal=True
        ),
        LabResult(
            test_name="eGFR",
            value="45",
            unit="mL/min/1.73m²",
            reference_range=">60",
            date="2024-01-15",
            is_abnormal=True
        )
    ]
    
    # Create comprehensive patient context
    patient = PatientContext(
        patient_id="P12345",
        patient_name="Rajesh Kumar",
        age=58,
        gender="Male",
        weight_kg=78.0,
        height_cm=172.0,
        chronic_conditions=["Type 2 Diabetes Mellitus", "Hypertension", "Stage 3 CKD"],
        allergies=["Penicillin", "Sulfa drugs"],
        past_surgeries=["Appendectomy (2010)", "Cholecystectomy (2015)"],
        family_history=["Father: CAD at age 55", "Mother: T2DM", "Brother: Hypertension"],
        current_medications=current_medications,
        latest_lab_results=lab_results,
        phone_number="+919876543210",
        preferred_language="en"
    )
    
    # Display patient information
    print(f"Patient ID: {patient.patient_id}")
    print(f"Name: {patient.patient_name}")
    print(f"Age: {patient.age} years, Gender: {patient.gender}")
    print(f"Weight: {patient.weight_kg} kg, Height: {patient.height_cm} cm")
    print(f"BMI: {patient.BMI:.1f} (Calculated)")
    print(f"Creatinine Clearance: {patient.creatinine_clearance:.1f} mL/min (Cockcroft-Gault)")
    print(f"\nChronic Conditions: {', '.join(patient.chronic_conditions)}")
    print(f"Allergies: {', '.join(patient.allergies)}")
    print(f"\nCurrent Medications:")
    for med in patient.current_medications:
        print(f"  • {med.name} {med.strength} ({med.frequency})")
    print(f"\nLatest Lab Results:")
    for lab in patient.latest_lab_results:
        flag = " ⚠️" if lab.is_abnormal else " ✓"
        print(f"  • {lab.test_name}: {lab.value} {lab.unit} (Ref: {lab.reference_range}){flag}")
    
    # ========================================================================
    # Step 2: New Prescription
    # ========================================================================
    print_section("Step 2: New Prescription")
    
    new_prescription = ExtractedPrescription(
        patient_id="P12345",
        symptoms=["fever", "cough", "body ache", "fatigue"],
        medicines=[
            Medicine(
                name="Ibuprofen",
                strength="400mg",
                frequency="1-1-1",
                instructions="Take after meals for 3 days",
                duration_days=3
            ),
            Medicine(
                name="Azithromycin",
                strength="500mg",
                frequency="1-0-0",
                instructions="Take before meals for 5 days",
                duration_days=5
            ),
            Medicine(
                name="Cetrizine",
                strength="10mg",
                frequency="0-0-1",
                instructions="Take at bedtime",
                duration_days=5
            )
        ],
        doctor_notes="Acute upper respiratory tract infection. Continue existing medications."
    )
    
    print(f"Symptoms: {', '.join(new_prescription.symptoms)}")
    print(f"\nNew Medicines Prescribed:")
    for med in new_prescription.medicines:
        print(f"  • {med.name} {med.strength}")
        print(f"    Frequency: {med.frequency}")
        print(f"    Instructions: {med.instructions}")
        print(f"    Duration: {med.duration_days} days\n")
    
    # ========================================================================
    # Step 3: Drug Interaction Checking
    # ========================================================================
    print_section("Step 3: Drug Interaction Checking")
    
    drug_checker = DrugInteractionChecker()
    
    # Combine current and new medications
    all_medicines = patient.current_medications + new_prescription.medicines
    
    print(f"Checking interactions for {len(all_medicines)} medications...")
    
    interactions = drug_checker.check_all_interactions(
        medicines=all_medicines,
        patient_context=patient
    )
    
    if interactions:
        print(f"\n⚠️  Found {len(interactions)} drug safety concerns:\n")
        
        for i, interaction in enumerate(interactions, 1):
            severity_icon = {
                "contraindicated": "🚫",
                "severe": "⚠️",
                "moderate": "⚡",
                "minor": "ℹ️"
            }.get(interaction.severity.lower(), "•")
            
            print(f"{severity_icon} {i}. {interaction.severity.upper()}: {interaction.drug1} + {interaction.drug2}")
            print(f"   Type: {interaction.interaction_type}")
            print(f"   {interaction.description}")
            print(f"   Recommendation: {interaction.recommendation}")
            print(f"   Source: {interaction.source}\n")
    else:
        print("✓ No significant drug interactions detected")
    
    # Check if human review needed
    critical_interactions = [i for i in interactions if i.severity in ["severe", "contraindicated"]]
    needs_review = len(critical_interactions) > 0
    
    if needs_review:
        print(f"\n⚠️  ALERT: {len(critical_interactions)} CRITICAL INTERACTIONS - HUMAN REVIEW REQUIRED")
    
    # ========================================================================
    # Step 4: Medication Schedule Generation
    # ========================================================================
    print_section("Step 4: Medication Schedule Generation")
    
    scheduler = get_schedule_generator()
    start_date = datetime.now().strftime("%Y-%m-%d")
    
    print(f"Generating medication schedule starting {start_date}...")
    
    schedules = scheduler.generate_schedule(
        medicines=new_prescription.medicines,
        patient_context=patient,
        start_date=start_date,
        interactions=interactions
    )
    
    print(f"\n✓ Generated schedules for {len(schedules)} medications\n")
    
    # Display detailed schedules
    for schedule in schedules:
        print(f"Medicine: {schedule.medicine.name} ({schedule.medicine.strength})")
        print(f"Duration: {schedule.duration_days} days")
        print(f"Scheduled Times: {', '.join(schedule.scheduled_times)}")
        print(f"Total Doses: {len(schedule.entries)}")
        print(f"Instructions: {schedule.medicine.instructions}\n")
    
    # Generate daily summary
    daily_summary = scheduler.generate_daily_summary(schedules, date=start_date)
    print(f"\n📅 Daily Medication Schedule:\n{daily_summary}")
    
    # ========================================================================
    # Step 5: Clinical Assessment
    # ========================================================================
    print_section("Step 5: Clinical Assessment")
    
    # Extract specific risks
    risks = [
        "Ibuprofen contraindicated in CKD Stage 3 - high risk of renal injury",
        "Dosage adjustment needed for Azithromycin due to reduced renal function",
        "Monitor blood glucose closely while on fever medications"
    ]
    
    if interactions:
        for interaction in critical_interactions:
            risks.append(f"{interaction.drug1} + {interaction.drug2}: {interaction.description}")
    
    # Create assessment
    assessment = ClinicalAssessment(
        risks_identified=risks,
        assessment_summary=(
            "Patient with T2DM, HTN, and Stage 3 CKD presenting with URTI symptoms. "
            "Critical concern: Ibuprofen is contraindicated in CKD. "
            "Recommend alternative analgesic (Paracetamol). "
            "Azithromycin requires dosage adjustment for renal function."
        ),
        triage_instructions=(
            "1. Switch Ibuprofen to Paracetamol 500mg 1-1-1\n"
            "2. Reduce Azithromycin to 250mg daily (50% dose reduction for CrCl 30-50)\n"
            "3. Monitor renal function in 1 week\n"
            "4. Continue existing diabetes and hypertension medications\n"
            "5. Adequate hydration recommended"
        ),
        red_flags=["Ibuprofen + CKD Stage 3", "Creatinine Clearance < 50 mL/min"],
        needs_human_review=needs_review,
        drug_interactions=interactions,
        dosage_warnings=[
            "Azithromycin: Reduce dose by 50% due to CrCl 30-50 mL/min",
            "Avoid NSAIDs in CKD - use Paracetamol instead"
        ]
    )
    
    print(f"Assessment Summary:\n{assessment.assessment_summary}\n")
    print(f"Risks Identified ({len(assessment.risks_identified)}):")
    for risk in assessment.risks_identified:
        print(f"  • {risk}")
    
    print(f"\nRed Flags:")
    for flag in assessment.red_flags:
        print(f"  🚩 {flag}")
    
    print(f"\nTriage Instructions:\n{assessment.triage_instructions}")
    
    print(f"\nDosage Warnings:")
    for warning in assessment.dosage_warnings:
        print(f"  ⚠️  {warning}")
    
    print(f"\nHuman Review Required: {'YES ⚠️' if assessment.needs_human_review else 'NO ✓'}")
    
    # ========================================================================
    # Step 6: RAG Cache Demo (Mocked)
    # ========================================================================
    print_section("Step 6: RAG Cache Performance")
    
    cache = get_rag_cache(enabled=True)
    
    if cache.health_check():
        print("✓ RAG Cache is operational\n")
        
        # Simulate cache operations
        query = "AIIMS guidelines for CKD patient with NSAID prescription"
        
        # First query (cache miss)
        print(f"Query: '{query}'")
        cached_result = cache.get(query, k=3)
        if cached_result:
            print("✓ Cache HIT - Retrieved in ~5ms")
        else:
            print("✗ Cache MISS - Querying database...")
            
            # Simulate DB query and cache storage
            mock_results = [
                {
                    "content": "NSAIDs are contraindicated in CKD Stage 3 and above...",
                    "metadata": {"source": "AIIMS_Nephrology_Guidelines.pdf", "page": 45}
                }
            ]
            cache.set(query, mock_results, k=3, ttl=3600)
            print("✓ Results cached for future queries (~600ms)")
        
        # Get cache stats
        stats = cache.get_stats()
        if "total_keys" in stats:
            print(f"\nCache Statistics:")
            print(f"  Total Keys: {stats.get('total_keys', 0)}")
            print(f"  Cache Hit Rate: {stats.get('hit_rate', 0):.1f}%")
    else:
        print("⚠️  RAG Cache is not available (Redis not running)")
        print("   Falling back to direct database queries")
    
    # ========================================================================
    # Step 7: Notification Summary
    # ========================================================================
    print_section("Step 7: WhatsApp Notification Summary")
    
    print(f"Patient: {patient.patient_name} ({patient.phone_number})")
    print(f"Language: {patient.preferred_language.upper()}\n")
    
    notifications_to_send = []
    
    if assessment.red_flags:
        notifications_to_send.append({
            "type": "CRITICAL ALERT",
            "message": f"⚠️ URGENT: Critical drug interaction detected. Please contact your doctor immediately."
        })
    
    if assessment.risks_identified:
        notifications_to_send.append({
            "type": "CLINICAL WARNING",
            "message": f"Important: Your prescription requires modifications due to your kidney function."
        })
    
    notifications_to_send.append({
        "type": "MEDICATION SCHEDULE",
        "message": daily_summary
    })
    
    print(f"Notifications to send: {len(notifications_to_send)}\n")
    for i, notif in enumerate(notifications_to_send, 1):
        print(f"{i}. {notif['type']}")
        print(f"   Preview: {notif['message'][:80]}...\n")
    
    print("✓ Notifications would be sent via Twilio WhatsApp API")
    print("  (Set ENABLE_NOTIFICATIONS=true in config to enable)")
    
    # ========================================================================
    # Summary
    # ========================================================================
    print_section("WORKFLOW SUMMARY")
    
    print("✅ Enhanced patient context created with demographics and labs")
    print(f"✅ {len(interactions)} drug interactions detected and analyzed")
    print(f"✅ Medication schedules generated for {len(schedules)} medicines")
    print(f"✅ Clinical assessment completed with {len(assessment.risks_identified)} risks identified")
    print(f"✅ {'Critical' if needs_review else 'Routine'} review status assigned")
    print(f"✅ {len(notifications_to_send)} notifications prepared for patient")
    
    if needs_review:
        print("\n⚠️  CRITICAL: Human review required before finalizing prescription")
    else:
        print("\n✓ Prescription safe to proceed with patient communication")
    
    print("\n" + "="*70)
    print("  Demo Complete - System Operating Normally")
    print("="*70 + "\n")


if __name__ == "__main__":
    print("\n" + "🏥 " * 20)
    print("    Medical AI Agent - Enhanced System Demo")
    print("🏥 " * 20 + "\n")
    
    asyncio.run(example_enhanced_workflow())
