import os
import json
from datasets import load_dataset

def download_musique():
    print("开始拉取真实数据集 MuSiQue (bdsaglam/musique) ...")
    try:
        # Load the validation or test set of MuSiQue
        dataset = load_dataset('bdsaglam/musique', split='validation')
        
        output_dir = 'data/musique'
        os.makedirs(output_dir, exist_ok=True)
        
        output_file = os.path.join(output_dir, 'validation.jsonl')
        with open(output_file, 'w', encoding='utf-8') as f:
            for item in dataset:
                json_record = {
                    "id": item.get("id"),
                    "question": item.get("question"),
                    "paragraphs": item.get("paragraphs"),
                    "answer": item.get("answer"),
                    "question_decomposition": item.get("question_decomposition")
                }
                f.write(json.dumps(json_record, ensure_ascii=False) + '\n')
                
        print(f"成功下载并处理了 {len(dataset)} 条真实多跳推理数据！")
        print(f"数据已保存至: {output_file}")
        
    except Exception as e:
        print(f"下载失败: {str(e)}")

if __name__ == '__main__':
    download_musique()
