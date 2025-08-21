from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import CustomUser, UserProfile


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer pour l'inscription des utilisateurs
    """
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = [
            'email', 'username', 'first_name', 'last_name', 
            'role', 'phone', 'password', 'password_confirm'
        ]

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Les mots de passe ne correspondent pas.")
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = CustomUser(**validated_data)
        user.set_password(password)
        user.save()
        
        # Créer le profil utilisateur
        UserProfile.objects.create(user=user)
        
        return user


class UserLoginSerializer(serializers.Serializer):
    """
    Serializer pour la connexion
    """
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(username=email, password=password)
            if not user:
                raise serializers.ValidationError('Email ou mot de passe incorrect.')
            if not user.is_active:
                raise serializers.ValidationError('Compte utilisateur désactivé.')
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError('Email et mot de passe requis.')


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer pour le profil utilisateur
    """
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_role = serializers.CharField(source='user.role', read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            'user_email', 'user_name', 'user_role', 'bio', 'linkedin_url',
            'github_url', 'website_url', 'skills', 'experience_years',
            'education_level', 'current_position', 'current_company',
            'salary_expectation', 'availability_date'
        ]


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer pour les données utilisateur
    """
    profile = UserProfileSerializer(read_only=True)
    full_name = serializers.CharField(source='get_full_name', read_only=True)

    class Meta:
        model = CustomUser
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name',
            'full_name', 'role', 'phone', 'birth_date', 'address',
            'profile_picture', 'is_verified', 'created_at', 'profile'
        ]
        read_only_fields = ['id', 'created_at', 'is_verified']


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer pour la mise à jour du profil utilisateur
    """
    profile = UserProfileSerializer(required=False)

    class Meta:
        model = CustomUser
        fields = [
            'first_name', 'last_name', 'phone', 'birth_date', 
            'address', 'profile_picture', 'profile'
        ]

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', None)
        
        # Mise à jour des données utilisateur
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Mise à jour du profil
        if profile_data:
            profile = instance.profile
            for attr, value in profile_data.items():
                setattr(profile, attr, value)
            profile.save()
        
        return instance
