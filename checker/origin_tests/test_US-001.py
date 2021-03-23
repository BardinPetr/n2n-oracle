import pytest

from docker_tools import start_container, stop_container


@pytest.mark.it('AC-001-01: Building the image.')
@pytest.mark.dependency(depends=[], name='AC_001_01', scope='session')
def test_AC_001_01(docker, log):
    log.info('Testing AC_001_01.')

    try:
        # $ docker build -t n2n-oracle .
        image, logs = docker.images.build( \
            path='./solution', tag='n2n-oracle')

    except Exception as exc:
        raise Exception(f'Exception while building the image:\n{exc}')

    # Build logs.
    log.debug('Solution build logs.')
    for line in logs:
        log.debug(line.get('stream', '')[:-1])

    # $ docker images | grep n2n-oracle
    assert docker.images.get('n2n-oracle').id == image.id, \
        f'Id images mismatch.'

    # $ docker run -ti n2n-oracle ls -la /deployment/run.sh
    container = start_container(docker, image, log, \
                                command=['ls', '-la', '/deployment/run.sh'])

    # Wait.
    container.wait(timeout=5)

    # Update state.
    container.reload()

    # Get exit code.
    exit_code = container.attrs['State']['ExitCode']

    # Delete container.
    stop_container(docker, container, log)

    # Should be ok.
    assert exit_code == 0, \
        f'Bad exit code: {exit_code}.'
