import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import { LoginPage } from '../src/pages/LoginPage';
import { AuthContext } from '../src/contexts/AuthContext';

describe('LoginPage', () => {
  it('submits credentials through context', async () => {
    const login = vi.fn().mockResolvedValue(undefined);
    render(
      <MemoryRouter>
        <AuthContext.Provider value={{ user: null, loading: false, login, logout: vi.fn() }}>
          <LoginPage />
        </AuthContext.Provider>
      </MemoryRouter>,
    );
    await userEvent.type(screen.getByLabelText(/email/i), 'a@b.c');
    await userEvent.type(screen.getByLabelText(/password/i), 'p@ss');
    await userEvent.click(screen.getByRole('button', { name: /sign in/i }));
    expect(login).toHaveBeenCalledWith('a@b.c', 'p@ss');
  });
});