from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2AuthorizationCodeBearer
from jose import JWTError, jwt
from app.config import Config
import httpx

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=f"https://{Config.AUTH0_DOMAIN}/authorize",
    tokenUrl=f"https://{Config.AUTH0_DOMAIN}/oauth/token",
    auto_error=False
)

async def get_current_user(token: str = Depends(oauth2_scheme)):
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    
    try:
        async with httpx.AsyncClient() as client:
            jwks = await client.get(f"https://{Config.AUTH0_DOMAIN}/.well-known/jwks.json")
            jwks = jwks.json()
        
        header = jwt.get_unverified_header(token)
        rsa_key = {}
        for key in jwks["keys"]:
            if key["kid"] == header["kid"]:
                rsa_key = {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key["use"],
                    "n": key["n"],
                    "e": key["e"]
                }
        
        if rsa_key:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=["RS256"],
                audience=Config.AUTH0_AUDIENCE,
                issuer=f"https://{Config.AUTH0_DOMAIN}/"
            )
            return payload
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
