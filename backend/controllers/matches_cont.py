from flask import Blueprint, request, g
from models.user_model import User
from serializers.populate_user_schema import PopulateUserSchema
from models.matches_model import Matches
from models.chat_model import Chats
from serializers.matches_schema import MatchesSchema
from serializers.chats_schema import ChatsSchema
from middleware.secure_route import secure_route

user_schema = PopulateUserSchema()
matches_schema = MatchesSchema()
chats_schema = ChatsSchema()

router = Blueprint(__name__, 'matches')

@router.route('/users/<int:user_id>/like', methods=['PUT'])
@secure_route
def like_user(user_id):
  liked_user = User.query.get(user_id)
  existing_matches = Matches.query.get(user_id)
  existing_curr_matches = Matches.query.get(g.current_user.id)


  if liked_user.id in existing_curr_matches.LikedBy :
    existing_matches.Matched.append(g.current_user.id)
    existing_curr_matches.Matched.append(user_id)
    existing_matches.save()
    existing_curr_matches.save()

    new_chat = Chats(
      user1 = g.current_user.id,
      user2 = liked_user.id,
      chat_history= ['The start of your chat']
    )

    liked_user.chats.append(new_chat)

    g.current_user.chats.append(new_chat)

    liked_user.save()
    g.current_user.save()

    return {'message': 'match!', 'id': f'{liked_user.id}'}, 200
  
  existing_matches.LikedBy.append(g.current_user.id)
  existing_curr_matches.Liked.append(user_id)

  existing_matches.save()
  existing_curr_matches.save()


  return user_schema.jsonify(liked_user), 200


@router.route('/users/<int:user_id>/dislike', methods=['PUT'])
@secure_route
def dislike_user(user_id):
  dislike_user = User.query.get(user_id)
  existing_matches = Matches.query.get(user_id)
  existing_curr_matches = Matches.query.get(g.current_user.id)

  existing_curr_matches.Disliked.append(user_id)

  existing_curr_matches.save()

  return user_schema.jsonify(g.current_user)

@router.route('/users/matches', methods=['GET'])
@secure_route
def get_matches():
  
  current_matches = Matches.query.get(g.current_user.id)
  return matches_schema.jsonify(current_matches)


@router.route('/users/<int:user_id>/removematch', methods=['PUT'])
@secure_route
def remove_match(user_id):
  current_user = g.current_user
  remove_user = User.query.get(user_id)

  curr_matches = Matches.query.get(current_user.id)
  remove_matches = Matches.query.get(remove_user.id)

  print(curr_matches.Matched)
  print(remove_matches.Matched)

  curr_matches.Matched.remove(remove_user.id)
  curr_matches.Disliked.append(remove_user.id)
  remove_matches.Matched.remove(current_user.id)
  remove_matches.Disliked.append(current_user.id)

  print(curr_matches.Matched)
  print(remove_matches.Matched)


  curr_matches.save()
  remove_matches.save()
  current_user.save()
  remove_user.save()

  return matches_schema.jsonify(curr_matches)
