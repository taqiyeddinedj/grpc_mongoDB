from concurrent import futures
import grpc
import user_management_pb2
import user_management_pb2_grpc
from pymongo import MongoClient
import pandas as pd
import bson

# MongoDB setup
client = MongoClient('localhost', 27017)
db = client.user_management
users = db.users

class UserManagementServicer(user_management_pb2_grpc.UserManagementServicer):

    def CreateUser(self, request, context):
        user = request.user
        result = users.insert_one({'name': user.name, 'email': user.email})
        new_user = users.find_one({'_id': result.inserted_id})
        return user_management_pb2.UserResponse(
            user=user_management_pb2.User(id=str(new_user['_id']), name=new_user['name'], email=new_user['email']),
            message="User created successfully."
        )

    def GetUser(self, request, context):
        user_id = request.id
        user = users.find_one({'_id': bson.ObjectId(user_id)})
        if user:
            return user_management_pb2.UserResponse(
                user=user_management_pb2.User(id=str(user['_id']), name=user['name'], email=user['email']),
                message="User retrieved successfully."
            )
        return user_management_pb2.UserResponse(
            message="User not found."
        )

    def UpdateUser(self, request, context):
        user = request.user
        result = users.update_one({'_id': bson.ObjectId(user.id)}, {"$set": {'name': user.name, 'email': user.email}})
        if result.matched_count:
            return user_management_pb2.UserResponse(
                user=user,
                message="User updated successfully."
            )
        return user_management_pb2.UserResponse(
            message="User not found."
        )

    def DeleteUser(self, request, context):
        user_id = request.id
        result = users.delete_one({'_id': bson.ObjectId(user_id)})
        if result.deleted_count:
            return user_management_pb2.UserResponse(
                message="User deleted successfully."
            )
        return user_management_pb2.UserResponse(
            message="User not found."
        )

    def ImportUsers(self, request, context):
        csv_file_path = request.csv_file_path
        try:
            data = pd.read_csv(csv_file_path)
            users_list = data.to_dict('records')
            result = users.insert_many(users_list)
            return user_management_pb2.ImportUsersResponse(
                imported_count=len(result.inserted_ids),
                message=f"Successfully imported {len(result.inserted_ids)} users."
            )
        except Exception as e:
            return user_management_pb2.ImportUsersResponse(
                imported_count=0,
                message=f"Failed to import users. Error: {str(e)}"
            )

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    user_management_pb2_grpc.add_UserManagementServicer_to_server(UserManagementServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
