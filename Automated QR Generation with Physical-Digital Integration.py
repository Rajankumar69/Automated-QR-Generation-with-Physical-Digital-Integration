import qrcode
import os
import numpy as np
from stl import mesh
from PIL import Image


def generate_qr_with_logo(url: str, logo_path: str, output_file: str = "qr_with_logo.png",
                          qr_color: str = "#000000", bg_color: str = "#FFFFFF",
                          logo_size_ratio: float = 0.2) -> None:
    """Generate 2D QR code with logo"""
    if not os.path.exists(logo_path):
        raise FileNotFoundError(f"Logo file not found at: {logo_path}")

    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4
    )
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill_color=qr_color, back_color=bg_color).convert('RGBA')
    logo = Image.open(logo_path).convert('RGBA')

    qr_width, qr_height = img.size
    logo_size = int(min(qr_width, qr_height) * logo_size_ratio)

    logo.thumbnail((logo_size, logo_size), Image.Resampling.LANCZOS)
    pos = ((qr_width - logo.size[0]) // 2, (qr_height - logo.size[1]) // 2)
    img.paste(logo, pos, logo)
    img.save(output_file)
    print(f"2D QR code saved as {output_file}")


def generate_3d_qr(url: str, output_stl: str = "qr_3d.stl",
                   module_size: float = 5.0, base_height: float = 1.0,
                   cube_height: float = 3.0) -> None:
    """Generate 3D printable QR code (STL format)"""
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4
    )
    qr.add_data(url)
    qr.make(fit=True)
    matrix = qr.get_matrix()

    rows, cols = len(matrix), len(matrix[0])

    # Create base plate
    base_vertices = np.array([
        [0, 0, 0], [cols * module_size, 0, 0], [cols * module_size, rows * module_size, 0],
        [0, rows * module_size, 0], [0, 0, base_height], [cols * module_size, 0, base_height],
        [cols * module_size, rows * module_size, base_height], [0, rows * module_size, base_height]
    ])

    base_faces = np.array([[0, 3, 1], [1, 3, 2], [0, 4, 7], [0, 7, 3], [1, 2, 6], [1, 6, 5],
                           [2, 3, 7], [2, 7, 6], [0, 1, 5], [0, 5, 4], [4, 5, 6], [4, 6, 7]])

    base_mesh = mesh.Mesh(np.zeros(base_faces.shape[0], dtype=mesh.Mesh.dtype))
    base_mesh.vectors = base_vertices[base_faces]

    # Create cubes for QR modules
    all_meshes = [base_mesh]
    for i in range(rows):
        for j in range(cols):
            if matrix[i][j]:
                x, y = j * module_size, i * module_size
                cube_verts = np.array([
                    [x, y, base_height], [x + module_size, y, base_height],
                    [x + module_size, y + module_size, base_height], [x, y + module_size, base_height],
                    [x, y, base_height + cube_height], [x + module_size, y, base_height + cube_height],
                    [x + module_size, y + module_size, base_height + cube_height],
                    [x, y + module_size, base_height + cube_height]
                ])
                cube = mesh.Mesh(np.zeros(12, dtype=mesh.Mesh.dtype))
                cube.vectors = cube_verts[base_faces]  # Reuse same face structure
                all_meshes.append(cube)

    combined = mesh.Mesh(np.concatenate([m.data for m in all_meshes]))
    combined.save(output_stl)
    print(f"3D printable QR saved as {output_stl}")


if __name__ == "__main__":
    # Generate both 2D and 3D versions
    logo_path = r"C:\Users\acer\OneDrive\Desktop\pythonproject\Automated QR Generation with Physical-Digital Integration\logo.png"

    generate_qr_with_logo(
        url="https://www.instagram.com/i_m_vengeance106/",
        logo_path=r"C:\Users\acer\OneDrive\Desktop\pythonproject\Automated QR Generation with Physical-Digital Integration\logo.png",
        output_file="instagram_qr.png",
        qr_color="#FF69B4",
        bg_color="#FFFFFF",
        logo_size_ratio=0.25
    )

    generate_3d_qr(
        url="https://www.instagram.com/i_m_vengeance106/",
        output_stl="instagram_qr_3d.stl",
        module_size=5.0,  # 5mm per QR module
        base_height=1.0,  # 1mm base thickness
        cube_height=3.0  # 3mm raised modules
    )