import graphene
from graphene_django import DjangoObjectType
from .models import Link,Vote
from hackernews.users.schema import UserType

class LinkType(DjangoObjectType):
    class Meta:
        model = Link
    
class VoteType(DjangoObjectType):
    class Meta:
        model = Vote

class Query(graphene.ObjectType):
    links = graphene.List(LinkType)
    votes = graphene.List(VoteType)

    def resolve_votes(self,info, **kwargs):
        return Vote.objects.all()

    def resolve_links(self,info,**kwargs):
        return Link.objects.all()

class CreateLink(graphene.Mutation):
    id = graphene.Int()
    url = graphene.String()
    description = graphene.String()
    posted_by = graphene.Field(UserType)

    class Arguments:
        url = graphene.String()
        description = graphene.String()

    def mutate(self,info,url,description):
        user = info.context.user or None
        link = Link(url=url,description = description)
        link.save()
        return CreateLink(url=link.url,description=link.description,posted_by = link.posted_by,)


class DeleteLink(graphene.Mutation):
    # id = graphene.Int()
    # url = graphene.String()
    # description = graphene.String()
    ok = graphene.Boolean()

    class Arguments:
        id = graphene.Int() 
    # info is used to send any info to the mutation during call
    def mutate(self,info, id):
        link = Link.objects.filter(id=id)
        #print("DEBUG: %s:%s:%s" % (link.id, link.description, link.url))
        link.delete()

        return DeleteLink(
            # id=id,  # Strangely using link.id here does yield the correct id
            # url=link.url,
            # description=link.description,
            ok = True
        )

class CreateVote(graphene.Mutation):
    user = graphene.Field(UserType)
    link = graphene.Field(LinkType)

    # Arguments is used to define what we have enter in mutation
    class Arguments:
        link_id = graphene.Int()
        
    #error handling
    def mutate(self,info,link_id):
        user = info.context.user
        print(user)
        if user.is_anonymous:
            raise Exception('you must be logged to vote')
        link = Link.objects.filter(id=link_id).first()

        if not link:
            raise Exception('Invalid link')

        Vote.objects.create(user=user,link=link,)
        return CreateVote(user=user, link= link)

class Mutation(graphene.ObjectType):
    create_link = CreateLink.Field()
    delete_link = DeleteLink.Field()
    create_vote = CreateVote.Field()