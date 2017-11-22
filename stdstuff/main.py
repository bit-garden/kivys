import subprocess

proc = subprocess.Popen(["python", "-c", "print('hello world')"], stdout=subprocess.PIPE)
out = proc.communicate()[0]
print(out.upper())