# This program outputs a few thousand characters of text.

def main():
    text = "DT is awesome! **** " * 200  # Each repetition is ~20 chars, 200*20 = 4000 chars
    print(text)

if __name__ == "__main__":
    main()

