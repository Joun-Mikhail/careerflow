import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';

import { PriorityBadge, StatusBadge } from './Badge';

describe('StatusBadge', () => {
  it('renders the humanized status label and status modifier class', () => {
    const { container } = render(<StatusBadge status="final_interview" />);
    expect(screen.getByText('Final Interview')).toBeInTheDocument();
    expect(container.querySelector('.badge--final_interview')).not.toBeNull();
  });
});

describe('PriorityBadge', () => {
  it('renders the priority label and modifier class', () => {
    const { container } = render(<PriorityBadge priority="high" />);
    expect(screen.getByText('High')).toBeInTheDocument();
    expect(container.querySelector('.badge--high')).not.toBeNull();
  });
});
