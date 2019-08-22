import app
from routes.index import profile
import cProfile
from pstats import Stats


def profile_request(path, cookie, f):
    a = app.configured_app()
    pr = cProfile.Profile()
    headers = {'Cookie': cookie}

    with a.test_request_context(path, headers=headers):
        pr.enable()

        # r = f()
        # assert type(r) == str, r
        f()

        pr.disable()

    # pr.dump_stats('gua_profile.out')
    # pr.create_stats()
    # s = Stats(pr)
    pr.create_stats()
    s = Stats(pr).sort_stats('cumulative')
    s.dump_stats('gua_profile.pstat')

    s.print_stats('.*web19.*')
    # s.print_callers()


if __name__ == '__main__':
    path = '/profile'
    cookie = '_ga=GA1.1.95897392.1561088843; session_id=2434b6a0-519c-4e00-b638-407976efe558; session=eyJfcGVybWFuZW50Ijp0cnVlLCJ1c2VyX2lkIjoxfQ.XSHkIw.sO1L74jpiQenBy85dPEERO18c2k'
    profile_request(path, cookie, profile)
