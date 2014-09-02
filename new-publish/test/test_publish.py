import os
import publib


def data_path():
#    return os.path.join(os.path.dirname(__file__), "data")
    return "test/data/"

def test_file_list1():
    l = publib.get_file_list([data_path() + "/*"])
    assert l == ['test/data/top_file'], l

def test_file_list2():
    l = publib.get_file_list([data_path() + "/*/*"])
    assert l == ['test/data/dir1/dir1_file', 'test/data/dir2/dir2_file'], l

def test_file_list3():
    d = data_path()
    l = publib.get_file_list([d + "/*", d + "/*/*"])
    assert l == ['test/data/top_file', 'test/data/dir1/dir1_file', 'test/data/dir2/dir2_file'], l

def test_file_list_order():
    d = data_path()
    l = publib.get_file_list([d + "*", d + "dir2/*", d + "dir1/*"])
    assert l == ['test/data/top_file', 'test/data/dir1/dir1_file', 'test/data/dir2/dir2_file'], l

def test_common_prefix():
    v = publib.common_path_prefix("a", "b")
    assert v == ([], ["a"]), v
    v = publib.common_path_prefix("a", "a")
    assert v == (["a"], []), v
    v = publib.common_path_prefix("a/c", "a/b")
    assert v == (["a"], ["c"]), v

def test_dir_creation():
    l = publib.make_dir_struct(["file1"], "/uploads")
    assert l == []
    l = publib.make_dir_struct(["file1", "dir2/f", "dir1/f"], "/uploads")
    assert l == ['/uploads/dir1', '/uploads/dir2'], l
    l = publib.make_dir_struct(["dir/subdir/f", "dir/f"], "/uploads")
    assert l == ['/uploads/dir', '/uploads/dir/subdir'], l
    l = publib.make_dir_struct(["dir/s1/s2/f", "dir/f"], "/uploads")
    assert l == ['/uploads/dir', '/uploads/dir/s1', '/uploads/dir/s1/s2'], l


def test_ftp_script_trivial():
    l = publib.make_upload_script(["file1"], "/uploads")
    assert l == ['cd /uploads', 'put file1'], l
    l = publib.make_upload_script(["dir/file1"], "/uploads")
    assert l == ['cd /uploads/dir', 'put dir/file1'], l


def test_validate_build_id():
    assert publib.validate_build_id("foo/bar")
    assert publib.validate_build_id("foo/bar-2.5")

    try:
        publib.validate_build_id("foo/bar/baz")
        assert False
    except SystemExit:
        pass

    try:
        publib.validate_build_id("foo/bar\\baz")
        assert False
    except SystemExit:
        pass

    try:
        publib.validate_build_id("../passwd")
        assert False
    except SystemExit:
        pass
