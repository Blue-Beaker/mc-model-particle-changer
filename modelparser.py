 
import copy,os,sys,regex
def getTextures(data:dict):
    if 'textures' in data:
        return data['textures']
    return {}
def getElements(data:dict):
    if 'elements' in data:
        return data['elements']
    return []
def getAllTextures(data:dict):
    textures=copy.deepcopy(getTextures(data))
    for i,element in enumerate(getElements(data)):
        if 'faces' in element:
            for dir in element['faces']:
                face=element['faces'][dir]
                if 'texture' in face:
                    textures["__e"+str(i)+"_"+dir]=face['texture']
    return textures

def getParticle(data:dict):
    if 'textures' in data:
        textures=data['textures']
        if 'particle' in textures:
            return textures['particle']
    return ''

def getRootDir(path:str):
    path=os.path.abspath(path)
    while not os.path.exists(os.path.join(path,"pack.mcmeta")):
        path=os.path.join(path,"..")
    return os.path.abspath(path)

def getTexturePath(pack:str,texture:str):
    split=texture.split(":",1)
    if len(split)==2:
        namespace=split[0]
        resourceid=split[1]
    else:
        namespace="minecraft"
        resourceid=texture
    return os.path.join(pack,"assets",namespace,"textures",resourceid+".png")

def lookupTexture(pack:str,texture:str,textures:dict):
    if texture.startswith("#"):
        return lookupTexture(pack,textures[texture[1:]],textures)
    return getTexturePath(pack,texture)