from fastapi import HTTPException

from app.repository.canje_repository import canjear_beneficio as canjear_beneficio_repo

def canjear_beneficio(
    id_persona: int,
    id_beneficio: int
):

    try:

        return canjear_beneficio_repo(
            id_persona,
            id_beneficio
        )

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
