"""
import paramiko

def deploy_to_device(device_ip, model_path):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(device_ip, username="user", password="password")
    sftp = ssh.open_sftp()
    sftp.put(model_path, "/path/on/device/model.tflite")
    sftp.close()
    ssh.close()
"""