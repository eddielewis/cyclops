import qrcode
import argparse
import os
import errno


def generate(id, output_folder, box_size, border, error_correction):
    code = qrcode.QRCode(
        # Gives 152, 128, 104, 72 bits for mixed data depending on error_c
        version=1,
        box_size=box_size,
        border=border,
        error_correction=error_correction
    )
    code.add_data(id)
    code.make(fit=False)
    img = code.make_image(fill_color="black", back_color="white")
    if output_folder != ".":
        try:
            os.makedirs(output_folder)
        except OSError as error:
            if error.errno != errno.EEXIST:
                raise
    img.save("%s/%d_%d_%d_%s.png" %
             (output_folder, id, box_size, border, error_correction))


def main():
    parser = argparse.ArgumentParser(
        description="Generates a QR code")
    parser.add_argument("--id",
                        help="An id number for the QR code.",
                        default=0,
                        type=int)
    parser.add_argument("--output_folder",
                        help="Path to folder to save codes in.",
                        default=".")
    parser.add_argument("--box_size",
                        help="The box_size parameter controls how many pixels each “box” of the QR code is. Default=10",
                        default=10,
                        type=int)
    parser.add_argument("--border",
                        help="The border parameter controls how many boxes thick the border should be. Default=0",
                        default=0,
                        type=int)
    parser.add_argument("--error_correction",
                        help="The error_correction parameter controls the error correction used for the QR Code (0-3). Default=1",
                        default=1,
                        type=int)
    args = parser.parse_args()

    generate(args.id, args.output_folder, args.box_size,
             args.border, args.error_correction)


if __name__ == "__main__":
    main()
