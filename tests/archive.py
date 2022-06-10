from unittest import TestCase
from unittest.mock import patch

from sitemanager.archive import make_gzipped_tarball
from tests.fakes import random_string


class ArchiveTests(TestCase):

    @patch("os.listdir")
    @patch("os.path")
    @patch("os.makedirs")
    def test_adds_files_to_gzipped_tarball(
            self, mock_makedirs, mock_path, mock_listdir):
        """
        Adds all files in a directory to a gzipped tarball.
        """
        dest_filepath = random_string(20)
        src_dirpath = random_string(20)
        src_filenames = [
            random_string(20),
            random_string(20)
        ]
        mock_listdir.return_value = src_filenames
        with patch("tarfile.open") as mock_tarfile_open:
            mock_tarball = mock_tarfile_open().__enter__.return_value
            make_gzipped_tarball(dest_filepath, src_dirpath)
        mock_tarball.add.assert_called()
        mock_listdir.assert_called_with(src_dirpath)
        mock_path.dirname.assert_called_with(dest_filepath)
        mock_path.join.assert_called()
        self.assertEqual(mock_path.join.call_count, 2)
        mock_makedirs.assert_called_with(
            mock_path.dirname.return_value, exist_ok=True)
