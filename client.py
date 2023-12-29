import grpc
import user_management_pb2
import user_management_pb2_grpc

def import_users(csv_file_path):
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = user_management_pb2_grpc.UserManagementStub(channel)
        response = stub.ImportUsers(user_management_pb2.ImportUsersRequest(csv_file_path=csv_file_path))
        print("ImportUsers Response:", response.message)

if __name__ == '__main__':
    csv_path = "path_to_your_csv_file.csv"  # Modify this path as needed
    import_users(csv_path)
