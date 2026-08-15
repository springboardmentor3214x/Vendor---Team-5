export const environment = {
  production: true,
  // Nginx proxies this path to the internal FastAPI container.  Never embed a
  // laptop hostname or an EC2 public IP into the production browser bundle.
  apiUrl: '/api'
};
