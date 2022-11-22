from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.password_validation import validate_password

from django.core import exceptions
from rest_framework import serializers

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={"input_type": "password"}, write_only=True)

    class Meta:
        model = User
        fields = ["email", "password", "password2"]
        extra_kwargs = {
            "password": {"write_only": True},
            "style": {"input_type": "password"},
        }

    def save(self):

        # here, self.validated_data is a dictionary

        password = self.validated_data["password"]

        # serializers.ModelSerializer doesn't render password2 field for User model on its own
        # unlike Django modelForm we have to provide an extra field for password2
        # so we have to add a password2 field in the serializer
        # since UserSerializer doesn't recognize password2 field as a User Model field
        # we need to pop or remove it from the self.validated_data
        # otherwise serializer will raise an error which simply means
        # password2 is not UserSerializer field
        password2 = self.validated_data.pop("password2")

        if password != password2:
            raise serializers.ValidationError({"error": "P1 and P2 should be same!"})

        if User.objects.filter(email=self.validated_data["email"]).exists():
            raise serializers.ValidationError({"error": "Email already exists!"})

        # in serializers we cannot user model.save(commit=False)
        # but we can use account = self.validated_data
        # which creates a User instance but doesn't save on the database
        # In other words its equivalent to model.save(commit=False)
        account = self.validated_data
        account = User(account)
        errors = {}
        try:
            # validate the password and catch the exception
            validate_password(password=password, user=account)

        # the exception raised here is different than serializers.ValidationError
        except exceptions.ValidationError as e:
            errors["password"] = list(e.messages)

        if errors:
            raise serializers.ValidationError(errors)

        # we can't use the following expression
        # account = self.validated_data
        # account = User(account)
        # If we try the above expression it will raise an error
        # and also it will not create any instance in the database
        # In order to create an User instance in the database
        # we need to use the following expression
        account = User(email=self.validated_data["email"])
        account.set_password(password)
        account.save()

        return account



# class AuthTokenSerializer(serializers.Serializer):
#     """Serializer for the user auth Token"""

#     email = serializers.EmailField()
#     password = serializers.CharField(
#         style={
#             "input_type": "password",
#         },
#         trim_whitespace=True,
#     )

#     def validate(self, attrs):
#         """Validate and authenticate the user"""
#         email = attrs.get("email")
#         password = attrs.get("password")
#         user = authenticate(username=email, password=password)
#         if not user:
#             msg = _(" Auth error: Unable to authenticate with  provided credentials")
#             raise serializers.ValidationError(msg, code="authorization")

#         # try:
#         #     user = authenticate(
#         #         # request=self.context.get("request"),
#         #         email=email,
#         #         password=password,
#         #     )

#         # except Exception as e:
#         #     raise e from e

#         attrs["user"] = user
#         return attrs