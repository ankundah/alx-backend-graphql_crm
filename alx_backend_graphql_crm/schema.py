import graphene

class Query(graphene.ObjectType):
    hello = graphene.String(default_value="Heyyyy Thia!")

schema = graphene.Schema(query=Query)
