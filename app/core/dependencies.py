from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt

from app.core.security import SECRET_KEY, ALGORITHM

security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    
    token = credentials.credentials
    
    try: 
        
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        
        username = payload.get("sub")
        
        if username is None:
            raise HTTPException(
                status_code = 401,
                detail = "Token inválido"
            )
            
        return payload
    
    except JWTError:
        
        raise HTTPException(
            status_code=401,
            detail="Token inválido o expirado"
        )
        
def require_admin(
    usuario = Depends(get_current_user)
):
    
    if usuario["rol"] != "admin":
        
        raise HTTPException(
            status_code=403,
            detail="No tienes permisos para realizar esta acción"
        )
    
    return usuario