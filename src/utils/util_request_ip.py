
def get_ip(app, request):
    """ Return remote LAN or WAN ip depending on dev/prod environnement
    """
    if (app.config['ENVNAME'] == 'Dev'):
        remote_ip = request.remote_addr # LAN ip 
    else:
        remote_ip = request.headers.get('X-Real-IP', '') # WAN ip 
    return (remote_ip)
