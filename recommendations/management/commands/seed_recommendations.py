import os
import json
from django.core.management.base import BaseCommand
from django.db import transaction
from django.conf import settings
from recommendations.models import Specialist, Disease, Medicine

class Command(BaseCommand):
    help = 'Seeds the database with medical specialists, disease knowledge base, and medicines'

    def handle(self, *args, **options):
        data_dir = os.path.join(settings.BASE_DIR, 'recommendations', 'data')
        
        specialists_file = os.path.join(data_dir, 'specialists.json')
        diseases_file = os.path.join(data_dir, 'disease_info.json')
        medicines_file = os.path.join(data_dir, 'medicines.json')

        if not os.path.exists(specialists_file) or not os.path.exists(diseases_file) or not os.path.exists(medicines_file):
            self.stderr.write(self.style.ERROR('Data files not found in recommendations/data/.'))
            return

        try:
            with transaction.atomic():
                # 1. Seed Specialists
                self.stdout.write('Seeding specialists...')
                with open(specialists_file, 'r', encoding='utf-8') as f:
                    specialists_data = json.load(f)
                
                for item in specialists_data:
                    Specialist.objects.update_or_create(
                        specialist=item['specialist'],
                        defaults={'description': item.get('description')}
                    )
                self.stdout.write(self.style.SUCCESS(f'Successfully seeded {len(specialists_data)} specialists.'))

                # 2. Seed Diseases
                self.stdout.write('Seeding diseases...')
                with open(diseases_file, 'r', encoding='utf-8') as f:
                    diseases_data = json.load(f)
                
                for disease_name, details in diseases_data.items():
                    Disease.objects.update_or_create(
                        disease_name=disease_name,
                        defaults={
                            'description': details['description'],
                            'precautions': details['precautions'],
                            'diet': details['diet'],
                            'home_remedies': details['home_remedies'],
                            'specialist': details['specialist']
                        }
                    )
                self.stdout.write(self.style.SUCCESS(f'Successfully seeded {len(diseases_data)} diseases.'))

                # 3. Seed Medicines
                self.stdout.write('Seeding medicines...')
                with open(medicines_file, 'r', encoding='utf-8') as f:
                    medicines_data = json.load(f)
                
                # Clear existing medicines to prevent duplicates
                Medicine.objects.all().delete()
                
                seeded_meds_count = 0
                for item in medicines_data:
                    try:
                        disease = Disease.objects.get(disease_name=item['disease_name'])
                        Medicine.objects.create(
                            disease=disease,
                            medicine_name=item['medicine_name'],
                            medicine_type=item['medicine_type'],
                            otc=item['otc'],
                            description=item['description'],
                            precautions=item.get('precautions', '')
                        )
                        seeded_meds_count += 1
                    except Disease.DoesNotExist:
                        self.stderr.write(self.style.WARNING(f"Disease '{item['disease_name']}' not found for medicine '{item['medicine_name']}'"))
                
                self.stdout.write(self.style.SUCCESS(f'Successfully seeded {seeded_meds_count} medicines.'))

        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Error seeding recommendations database: {e}'))
