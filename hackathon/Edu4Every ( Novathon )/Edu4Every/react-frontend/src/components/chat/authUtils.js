// authUtils.js
export const CUSTOMER_SERVICE_EMAILS = [
  { email: 'edu4every@gmail.com', password: 'edu123' }
];

export const getGreeting = () => {
  const hour = new Date().getHours();
  if (hour < 12) return 'Good morning';
  if (hour < 18) return 'Good afternoon';
  return 'Good evening';
};