import { Outlet, NavLink } from 'react-router-dom';

export default function RootLayout() {
  return (
    <div className="min-h-screen bg-white text-gray-900 flex flex-col">
      <header className="border-b border-gray-200 px-8 py-4 flex items-center justify-between">
        <div className="text-lg font-semibold tracking-tight">App</div>
        <nav className="flex gap-6 text-sm font-medium">
          <NavLink
            to="/"
            end
            className={({ isActive }) =>
              isActive ? 'text-black underline' : 'text-gray-600 hover:text-black'
            }
          >
            Landing
          </NavLink>
          <NavLink
            to="/live-monitor"
            className={({ isActive }) =>
              isActive ? 'text-black underline' : 'text-gray-600 hover:text-black'
            }
          >
            Live Monitor
          </NavLink>
          <NavLink
            to="/analytics"
            className={({ isActive }) =>
              isActive ? 'text-black underline' : 'text-gray-600 hover:text-black'
            }
          >
            Analytics
          </NavLink>
        </nav>
      </header>
      <main className="flex-1">
        <Outlet />
      </main>
    </div>
  );
}
