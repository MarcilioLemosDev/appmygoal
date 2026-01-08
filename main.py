import flet as ft

def main(page: ft.Page):
    # Configurações da Janela
    page.title = "App MyGoal"
    page.window.width = 400      
    page.window.height = 700      
    page.window.resizable = False 
    page.theme_mode = ft.ThemeMode.LIGHT 
    page.vertical_alignment = ft.MainAxisAlignment.CENTER 

    # Texto de teste
    titulo = ft.Text(
        value="MyGoal Iniciado!", 
        size=30, 
        color="blue",  # <--- MUDAMOS AQUI (Texto simples funciona sempre)
        weight=ft.FontWeight.BOLD
    )

    page.add(titulo)

if __name__ == "__main__":
    ft.app(target=main)