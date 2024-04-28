 
import copy,os,sys,regex
import traceback
import json
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
                    tex=face['texture']
                    if tex.removeprefix("#") not in textures:
                        textures[tex]="[Parent]"
                    # textures["__e"+str(i)+"_"+dir]=face['texture']
    return textures

def getParticle(data:dict):
    if 'textures' in data:
        textures=data['textures']
        if 'particle' in textures:
            return textures['particle']
    return None

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

def getModelPath(pack:str,model:str):
    split=model.split(":",1)
    if len(split)==2:
        namespace=split[0]
        resourceid=split[1]
    else:
        namespace="minecraft"
        resourceid=model
    return os.path.join(pack,"assets",namespace,"models",resourceid+".json")


def getResourceLocation(pack:str,texturePath:str):
    path=texturePath.removeprefix(pack)
    path=path.removeprefix("/assets/").removesuffix(".png")
    if "/textures/" in path:
        split=path.split("/textures/")
    elif "/models/" in path:
        split=path.split("/models/")
    else:
        return texturePath
    if split[0]!="minecraft":
        return split[0]+":"+split[1]
    else:
        return split[1]

def lookupTexture(pack:str,texture:str,textures:dict):
    if texture.startswith("#"):
        tex=texture[1:]
        if tex in textures:
            return lookupTexture(pack,textures[tex],textures)
    return getTexturePath(pack,texture)

def lookupParent(pack:str,data:dict):
    if "parent" in data:
        return getModelPath(pack,data["parent"])
    
def lookupParentParticle(pack:str,data:dict):
    try:
        particle=getParticle(data)
        if particle:
            return particle
        parent=lookupParent(pack,data)
        if parent:
            with open(parent,"r") as f:
                    return lookupParentParticle(pack,json.load(f))
    except:
        traceback.print_exc()

def setParticle(particle:str,data:dict):
    data2=copy.deepcopy(data)
    if not 'texture' in data2:
        data2['texture']={}
    data2['texture']['particle']=particle
    return data2

def readFile(path:str):
    with open(path,"r") as f:
        return json.load(f)

def writeFile(path:str,data:dict,overwrite:bool=False):
    if os.path.exists(path) and not overwrite:
        return
    with open(path,"r") as f:
        json.dump(data,f,indent=2)