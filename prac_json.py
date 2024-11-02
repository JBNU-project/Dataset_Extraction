from psd_tools import PSDImage
import os
import json


def find_and_extract_layers(psd_file, output_dir, json_output):
    # PSD 파일 열기
    psd = PSDImage.open(psd_file)
    # 출력 디렉토리가 없으면 생성
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # JSON 데이터를 저장할 리스트
    annotations = []
    image_id = os.path.splitext(os.path.basename(psd_file))[0]

    group_layers = [layer for layer in psd._layers if hasattr(layer, 'descendants')]
    group_layers = filter(lambda layer: layer.name == '효과음', group_layers)

    for layer_id, _layer in enumerate(group_layers):
        print(f"Group: {_layer.name}")
        for layer in _layer:
            # 레이어 정보 가져오기
            layer_name = layer.name
            layer_bbox = layer.bbox

            if isinstance(layer_bbox, tuple) and len(layer_bbox) == 4:
                left, top, right, bottom = layer_bbox
                width = right - left
                height = bottom - top
            else:
                left, top, right, bottom = 0, 0, 0, 0
                width, height = 0, 0

            if layer.is_visible() and layer.has_pixels():
                # 레이어 정보를 JSON 형식에 맞게 추가
                annotation = {
                    "bbox": {
                        "x": left,
                        "y": top,
                        "width": width,
                        "height": height
                    },
                    "text": layer_name,
                }
                annotations.append(annotation)

                layer_image = layer.composite()
                base_name = ''.join(c for c in layer_name if c.isalnum() or c in (' ', '_', '-'))
                output_path = os.path.join(output_dir, f"{base_name}.png")
                count = 1
                while os.path.exists(output_path):
                    output_path = os.path.join(output_dir, f"{base_name}_{count}.png")
                    count += 1
                layer_image.save(output_path)
                print(f"  Extracted: {output_path}")

    # JSON 파일로 저장
    json_data = {"annotations": annotations}
    with open(json_output, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, ensure_ascii=False, indent=4)
    print(f"JSON data saved to {json_output}")


# 사용 예시
psd_file = '01 - (6).psd'
output_directory = 'outputs'
json_output_file = 'output_annotations.json'
find_and_extract_layers(psd_file, output_directory, json_output_file)
