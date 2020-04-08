from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
import graphene
from graphene_django import DjangoObjectType

class UserType(DjangoObjectType):
    class Meta:
        model = get_user_model()

class Query(graphene.ObjectType):
    obj = graphene.List(UserType)
    me = graphene.Field(UserType)

    def resolve_obj(self, info):
        return User.objects.all()
    
    def resolve_me(self,info):
        user = info.context.user
        if user.is_anonymous:
            raise Exception('Not Logged in!')
        return user
    
class createUser(graphene.Mutation):
    user = graphene.Field(UserType)
    class Arguments:
        email = graphene.String(required = True)
        password = graphene.String(required=True)
        username = graphene.String(required=True)

    def mutate(self, info,username,password,email):
        user = get_user_model()(username=username,email=email)
        user.set_password(password)
        user.save()
        return createUser(user=user)


class Mutation(graphene.ObjectType):
    create_user = createUser.Field()
