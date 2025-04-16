from shiny import App, ui, render

app_ui = ui.page_fluid(
    ui.input_slider("n", "Pilih angka:", 1, 100, 10),
    ui.output_text_verbatim("text")
)

def server(input, output, session):
    @output()
    @render.text
    def text():
        return f"Kamu pilih angka: {input.n()}"

app = App(app_ui, server)
