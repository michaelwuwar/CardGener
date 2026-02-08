from cardconjurer_automation import CardConjurerAutomation
from pathlib import Path

files = [str(p) for p in Path('test_output').glob('*.json')]
print('will process', files)
automation = CardConjurerAutomation(headless=True, download_dir='downloaded_images')
print('starting batch...')
count = automation.batch_import_and_download(files)
print('result count:', count)
