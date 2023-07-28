# injection-attack-analysis
Injection attack analysis on a android mobile application to simulate a vulnerable sequence and a Python Docker server to add defense module to prevent injection attacks.

1- Launch Docker Container and make an image of the server, launch it, ready to receive single or multiple base64 images under JSON sending format.

2- Requests example (only POST):

Single image:

´´´json
{
    "str64_image": "base64 image"
}
´´´

Multiple images:

´´´json
{
    "listStr64_image": ["first base64 image", ..., "last base64 image"]
}
´´´


3- Install the android application and modify the sending ip-address with the docker server one.

You now have a vulnerable sequence to injection attack. 

