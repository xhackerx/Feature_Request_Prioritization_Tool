import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType
from .models import FeatureRequest as FeatureRequestModel

class FeatureRequest(SQLAlchemyObjectType):
    class Meta:
        model = FeatureRequestModel

class Query(graphene.ObjectType):
    features = graphene.List(FeatureRequest)
    feature = graphene.Field(FeatureRequest, id=graphene.Int(required=True))
    
    def resolve_features(self, info):
        return FeatureRequestModel.query.all()
    
    def resolve_feature(self, info, id):
        return FeatureRequestModel.query.get(id)

class CreateFeatureInput(graphene.InputObjectType):
    title = graphene.String(required=True)
    description = graphene.String(required=True)
    user_impact = graphene.Int(required=True)
    effort_required = graphene.Int(required=True)
    strategic_alignment = graphene.Int(required=True)

class CreateFeature(graphene.Mutation):
    class Arguments:
        input = CreateFeatureInput(required=True)
    
    feature = graphene.Field(FeatureRequest)
    
    def mutate(self, info, input):
        feature = FeatureRequestModel(
            title=input.title,
            description=input.description,
            user_impact=input.user_impact,
            effort_required=input.effort_required,
            strategic_alignment=input.strategic_alignment
        )
        feature.calculate_priority_score()
        db.session.add(feature)
        db.session.commit()
        return CreateFeature(feature=feature)

class UpdateFeature(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        input = CreateFeatureInput(required=True)
    
    feature = graphene.Field(FeatureRequest)
    
    def mutate(self, info, id, input):
        feature = FeatureRequestModel.query.get(id)
        if not feature:
            raise Exception('Feature not found')
        
        feature.title = input.title
        feature.description = input.description
        feature.user_impact = input.user_impact
        feature.effort_required = input.effort_required
        feature.strategic_alignment = input.strategic_alignment
        feature.calculate_priority_score()
        
        db.session.commit()
        return UpdateFeature(feature=feature)

class DeleteFeature(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
    
    success = graphene.Boolean()
    
    def mutate(self, info, id):
        feature = FeatureRequestModel.query.get(id)
        if not feature:
            raise Exception('Feature not found')
        
        db.session.delete(feature)
        db.session.commit()
        return DeleteFeature(success=True)

class Mutation(graphene.ObjectType):
    create_feature = CreateFeature.Field()
    update_feature = UpdateFeature.Field()
    delete_feature = DeleteFeature.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)