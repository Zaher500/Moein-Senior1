import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  vus: 5,
  duration: '20s',
};

const audioData = open('./techno.m4a', 'b');

export default function () {
  const url = 'http://127.0.0.1:8007/stt/upload/';

  const payload = {
    audio: http.file(audioData, 'techno.m4a', 'audio/mp4'),
  };

  const params = {
    headers: {
      'X-Student-ID': 'student-123',
      'X-User-ID': 'user-123',
    },
  };

  const res = http.post(url, payload, params);

  check(res, {
    'status is 202': (r) => r.status === 202,
  });

  sleep(1);
}