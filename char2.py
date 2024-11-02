from psd_tools import PSDImage
from PIL import Image
import os

def find_and_extract_layers(psd_file, output_dir):
    # PSD 파일 열기
    psd = PSDImage.open(psd_file)
    # 출력 디렉토리가 없으면 생성
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # '캐릭터' 그룹을 재귀적으로 찾기
    def find_character_groups(layers):
        character_groups = []
        for layer in layers:
            if hasattr(layer, 'descendants') and layer.is_group():
                if layer.name == '캐릭터':
                    character_groups.append(layer)
                else:
                    character_groups.extend(find_character_groups(layer))
        return character_groups

    character_groups = find_character_groups(psd)

    def get_unique_filename(base_path):
        """Return a unique file path by adding a numeric suffix if needed."""
        if not os.path.exists(base_path):
            return base_path
        else:
            base, ext = os.path.splitext(base_path)
            counter = 1
            new_path = f"{base}_{counter}{ext}"
            while os.path.exists(new_path):
                counter += 1
                new_path = f"{base}_{counter}{ext}"
            return new_path

    for character_group in character_groups:
        print(f"Character Group: {character_group.name}")

        for sub_group in character_group:
            if not hasattr(sub_group, 'descendants'):
                continue

            sub_group_name = sub_group.name
            sub_group_bbox = sub_group.bbox

            # 레이어 그룹 정보 출력
            print("2")
            print(f"\tSub Group: {sub_group_name}")

            if isinstance(sub_group_bbox, tuple) and len(sub_group_bbox) == 4:
                left, top, right, bottom = sub_group_bbox
                width = right - left
                height = bottom - top
            else:
                left, top, right, bottom = 0, 0, 0, 0
                width, height = 0, 0

            print(f"\t\tPosition: left={left}, top={top}, right={right}, bottom={bottom}")
            print(f"\t\tSize: width={width}, height={height}")

            # 서브 그룹 내 모든 레이어가 있는지 확인
            if sub_group.is_visible():
                # 레이어 그룹을 이미지로 변환
                group_image = sub_group.composite()

                # 안전한 파일명 생성
                safe_name = ''.join(c for c in sub_group_name if c.isalnum() or c in (' ', '_', '-'))
                output_path = os.path.join(output_dir, f"{safe_name}.png")

                # Ensure a unique filename to avoid overwriting
                unique_output_path = get_unique_filename(output_path)
                
                # PNG 파일로 저장
                group_image.save(unique_output_path)
                print(f"  Extracted: {unique_output_path}")

# 사용 예시
psd_file = '009.psd'
output_directory = 'outputs'
find_and_extract_layers(psd_file, output_directory)
