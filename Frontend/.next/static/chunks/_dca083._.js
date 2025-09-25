(globalThis.TURBOPACK = globalThis.TURBOPACK || []).push(["static/chunks/_dca083._.js", {

"[project]/contexts/AuthContext.tsx [app-client] (ecmascript)": (({ r: __turbopack_require__, f: __turbopack_module_context__, i: __turbopack_import__, s: __turbopack_esm__, v: __turbopack_export_value__, n: __turbopack_export_namespace__, c: __turbopack_cache__, M: __turbopack_modules__, l: __turbopack_load__, j: __turbopack_dynamic__, P: __turbopack_resolve_absolute_path__, U: __turbopack_relative_url__, R: __turbopack_resolve_module_id_path__, g: global, __dirname, k: __turbopack_refresh__ }) => (() => {
"use strict";

__turbopack_esm__({
    "AuthProvider": ()=>AuthProvider,
    "useAuth": ()=>useAuth
});
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/node_modules/next/dist/compiled/react/jsx-dev-runtime.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/node_modules/next/dist/compiled/react/index.js [app-client] (ecmascript)");
"__TURBOPACK__ecmascript__hoisting__location__";
;
var _s = __turbopack_refresh__.signature(), _s1 = __turbopack_refresh__.signature();
'use client';
;
const AuthContext = /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["createContext"])(undefined);
const useAuth = ()=>{
    _s();
    const context = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useContext"])(AuthContext);
    if (context === undefined) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
};
_s(useAuth, "b9L3QQ+jgeyIrH0NfHrJ8nn7VMU=");
const AuthProvider = ({ children })=>{
    _s1();
    const [user, setUser] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(null);
    const [token, setToken] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(null);
    const [isLoading, setIsLoading] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(true);
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useEffect"])(()=>{
        // Verificar si hay un token almacenado
        const storedToken = localStorage.getItem('access_token');
        if (storedToken) {
            setToken(storedToken);
            // Verificar token con el backend
            verifyToken(storedToken);
        } else {
            setIsLoading(false);
        }
    }, []);
    const verifyToken = async (token)=>{
        try {
            const response = await fetch('http://localhost:8002/api/auth/me', {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Origin': window.location.origin
                }
            });
            if (response.ok) {
                const data = await response.json();
                setUser(data.user);
            } else {
                // Token inválido, limpiar
                localStorage.removeItem('access_token');
                setToken(null);
                setUser(null);
            }
        } catch (error) {
            console.error('Error verificando token:', error);
            localStorage.removeItem('access_token');
            setToken(null);
            setUser(null);
        } finally{
            setIsLoading(false);
        }
    };
    const login = async (username, password)=>{
        try {
            const response = await fetch('http://localhost:8002/api/auth/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Origin': window.location.origin
                },
                body: JSON.stringify({
                    identifier: username,
                    password
                })
            });
            const data = await response.json();
            if (response.ok && data.access_token) {
                const userData = data.user || {
                    id: '1',
                    username: username,
                    email: '',
                    role: 'user'
                };
                const authToken = data.access_token;
                const message = data.message || 'Inicio de sesión exitoso';
                setUser(userData);
                setToken(authToken);
                localStorage.setItem('access_token', authToken);
                return {
                    success: true,
                    message: message || 'Inicio de sesión exitoso'
                };
            } else {
                return {
                    success: false,
                    message: data.message || 'Credenciales inválidas'
                };
            }
        } catch (error) {
            console.error('Error en login:', error);
            return {
                success: false,
                message: 'Error de conexión'
            };
        }
    };
    const register = async (username, email, password)=>{
        try {
            const response = await fetch('http://localhost:8002/api/auth/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Origin': window.location.origin
                },
                body: JSON.stringify({
                    username,
                    email,
                    password
                })
            });
            const data = await response.json();
            if (response.ok && !data.error) {
                return {
                    success: true,
                    message: 'Usuario registrado exitosamente. Ahora puedes iniciar sesión.'
                };
            } else {
                return {
                    success: false,
                    message: data.error || 'Error al registrar usuario'
                };
            }
        } catch (error) {
            console.error('Error en registro:', error);
            return {
                success: false,
                message: 'Error de conexión'
            };
        }
    };
    const logout = ()=>{
        setUser(null);
        setToken(null);
        localStorage.removeItem('access_token');
    };
    const value = {
        user,
        token,
        login,
        register,
        logout,
        isLoading,
        isAuthenticated: !!user && !!token
    };
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(AuthContext.Provider, {
        value: value,
        children: children
    }, void 0, false, {
        fileName: "[project]/contexts/AuthContext.tsx",
        lineNumber: 154,
        columnNumber: 5
    }, this);
};
_s1(AuthProvider, "mX4/AXRUN66G8j/NKXHYWKblzjI=");
_c = AuthProvider;
var _c;
__turbopack_refresh__.register(_c, "AuthProvider");

})()),
"[project]/app/layout.tsx [app-rsc] (ecmascript, Next.js server component, client modules)": (({ r: __turbopack_require__, f: __turbopack_module_context__, i: __turbopack_import__, s: __turbopack_esm__, v: __turbopack_export_value__, n: __turbopack_export_namespace__, c: __turbopack_cache__, M: __turbopack_modules__, l: __turbopack_load__, j: __turbopack_dynamic__, P: __turbopack_resolve_absolute_path__, U: __turbopack_relative_url__, R: __turbopack_resolve_module_id_path__, g: global, __dirname }) => (() => {


})()),
}]);

//# sourceMappingURL=_dca083._.js.map