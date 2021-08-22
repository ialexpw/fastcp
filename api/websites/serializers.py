from rest_framework import serializers
from core.models import Website, Domain
import validators
from core import signals


class ChangePhpVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Website
        fields = ['php']
  
class DomainSerializer(serializers.ModelSerializer):
    class Meta:
        model = Domain
        fields = '__all__'
    
    def validate_domain(self, value):
        """Ensure that the value is a valid domain"""
        if not validators.domain(value):
            raise serializers.ValidationError(f'{value} is not a valid domain.')
        
        # A domain should always be lower case
        if value:
            value = value.lower()
        return value

class WebsiteSerializer(serializers.ModelSerializer):
    domains = DomainSerializer(many=True, required=False)
    class Meta:
        model = Website
        fields = ['id', 'label', 'user', 'metadata', 'domains', 'has_ssl', 'php']
        read_only_fields = ['id', 'has_ssl', 'domains', 'metadata', 'domains', 'user']
        
    
    def validate_domains(self, value):
        # Validate domains
        domains = list(filter(None, [domain.strip() for domain in value.strip().split(',')]))
        if len(domains) == 0:
            raise serializers.ValidationError({'domains': ['You have not provided any domains.']})
        else:
            for domain in domains:
                # Check if domain is valid
                if not validators.domain(domain):
                    raise serializers.ValidationError({'domains': [f'{domain} is not a valid domain.']})
                
                # Ensure domain is unique
                if Domain.objects.filter(domain=domain).count():
                    raise serializers.ValidationError({'domains': [f'{domain} already exists in the database.']})
        
        return domains

    def create(self, validated_data):
        request = self.context['request']
        domains = request.POST.get('domains')
        domains = self.validate_domains(domains)
        user = request.user
        validated_data['user'] = user
        website = Website.objects.create(**validated_data)
        
        # Create domains
        for domain in domains:
            website.domains.create(
                domain=domain
            )
        
        # Send domains updated signal so vhost file
        # will be created.
        signals.domains_updated.send(sender=website)
        return website