import re
import clipboard

class LatexPDFtoPlainText:
    def run(self):
        r = ''
        while r.lower()!='x':
            self._process()
            r = input("Press any key to process clipboard or 'x' to exit: ")
    #
    def _process(self):
        text = clipboard.paste()
        resultado = re.sub(r'\.\n', '.\n\n', text)
        resultado = re.sub(r'(?<!\n)\n(?!\n)', ' ', resultado)
        resultado = re.sub(r'^(\d{1,2}\. )', r'\n \1', resultado, flags=re.MULTILINE)
        resultado = resultado.replace('- ', '')
        clipboard.copy(resultado)
        #
        print("Processed text copied to clipboard")



def main():
    convert = LatexPDFtoPlainText()
    convert.run()

if __name__ == "__main__":
    main()
