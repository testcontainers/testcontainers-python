
from pathlib import Path
from os import path
import tarfile
import tempfile
from contextlib import contextmanager

@contextmanager
def file(container, target):
	target_path = Path(target)
	assert target_path.is_absolute(), "target must be an absolute path"

	with tempfile.TemporaryDirectory() as tmpdirname:
		archive = Path(tmpdirname) / 'grabbed.tar'

		# download from container as tar archive
		with open(archive, 'wb') as f:
			tar_bits, _ = container.get_archive(target)
			for chunk in tar_bits:
				f.write(chunk)

		# extract target file from tar archive
		with tarfile.TarFile(archive) as tar:
			yield tar.extractfile(path.basename(target))

