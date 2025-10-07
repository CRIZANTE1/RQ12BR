"""
Módulo de notificações por email (stub temporário)
TODO: Implementar integração real com serviço de email
"""

def notify_new_access_request(admin_email, user_email, user_name, justification):
    """
    Notifica admin sobre nova solicitação de acesso
    
    Args:
        admin_email: Email do administrador
        user_email: Email do usuário solicitante
        user_name: Nome do usuário
        justification: Justificativa da solicitação
        
    Returns:
        bool: False (implementação pendente)
    """
    # TODO: Implementar envio de email
    print(f"[STUB] Notificação de solicitação: {user_name} ({user_email})")
    return False


def notify_access_approved(user_email, user_name, trial_days=14):
    """
    Notifica usuário sobre aprovação de acesso
    
    Args:
        user_email: Email do usuário
        user_name: Nome do usuário
        trial_days: Dias de trial concedidos
        
    Returns:
        bool: False (implementação pendente)
    """
    # TODO: Implementar envio de email
    print(f"[STUB] Notificação de aprovação: {user_name} ({user_email}) - {trial_days} dias")
    return False


def notify_access_denied(user_email, user_name, reason=None):
    """
    Notifica usuário sobre rejeição de acesso
    
    Args:
        user_email: Email do usuário
        user_name: Nome do usuário
        reason: Motivo da rejeição (opcional)
        
    Returns:
        bool: False (implementação pendente)
    """
    # TODO: Implementar envio de email
    print(f"[STUB] Notificação de rejeição: {user_name} ({user_email})")
    if reason:
        print(f"    Motivo: {reason}")
    return False