import sys, os
os.chdir('/media/data3/dengkw/idea04/external_baselines/reagent')
sys.path.insert(0, '.')

# Before importing ReAgent modules we need config/env.yaml; write a stub if missing.
from pathlib import Path
cfg_dir = Path('config')
cfg_dir.mkdir(parents=True, exist_ok=True)
env_yaml = cfg_dir / 'env.yaml'
if not env_yaml.is_file():
    env_yaml.write_text(
        "services:\n"
        "  openai:\n"
        "    api_key: stub\n"
        "    base_url: https://stub.invalid\n"
        "  qwen:\n    api_key: stub\n    base_url: https://stub.invalid\n"
        "  deepseek:\n    api_key: stub\n    base_url: https://stub.invalid\n"
        "  claude:\n    api_key: stub\n    base_url: https://stub.invalid\n",
        encoding='utf-8',
    )

errors = []
try:
    from Agent.moderator2 import Moderator2
except Exception as e:
    errors.append(('Moderator2', repr(e)))
try:
    from Agent.agent import BaseAgent
except Exception as e:
    errors.append(('BaseAgent', repr(e)))
try:
    from Agent.blacksheep import BlackSheep
except Exception as e:
    errors.append(('BlackSheep', repr(e)))
try:
    from Agent.thinker import Thinker
except Exception as e:
    errors.append(('Thinker', repr(e)))
try:
    from Agent.human import Human
except Exception as e:
    errors.append(('Human', repr(e)))
try:
    from Environment.groupchat import GroupChatEnvironment
except Exception as e:
    errors.append(('GroupChatEnvironment', repr(e)))
try:
    from DataProcess.Dataset import HotpotqaDataset
except Exception as e:
    errors.append(('HotpotqaDataset', repr(e)))
if errors:
    print("IMPORT FAILURES:")
    for name, err in errors:
        print(f"  - {name}: {err}")
    sys.exit(1)
print("OK — all ReAgent modules importable under venv_reagent")
