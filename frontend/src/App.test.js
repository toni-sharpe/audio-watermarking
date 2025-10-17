import { render, screen } from '@testing-library/react';
import App from './App';

test('renders audio watermarking app', () => {
  render(<App />);
  const headingElement = screen.getByText(/Audio Watermarking Tool/i);
  expect(headingElement).toBeInTheDocument();
});
