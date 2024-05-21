export interface Message {
  text: string;
  sender: string;
  username: string;
  isLoading?: boolean; // Optional property to handle loading state
}
