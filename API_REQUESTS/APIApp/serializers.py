from rest_framework import serializers
from APIApp.models import User, Profile

class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'level', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
    
    def to_representation(self, instance):
        # Customize the representation of the User object as needed
        representation = super().to_representation(instance)
        representation['password'] = instance.password
        return representation

class UserLoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255)
    class Meta:
        model = User
        fields = ['email', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['name', 'designation', 'address', 'phone_no', 'salary']

class ProfileRequestSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    designation = serializers.CharField(max_length=255)
    address = serializers.CharField(max_length=255)
    phone_no = serializers.CharField(max_length=15)
    salary = serializers.DecimalField(max_digits=10, decimal_places=2)
    token = serializers.CharField()
