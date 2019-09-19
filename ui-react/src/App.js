import React, { useEffect, useState } from "react";
import "./App.css";
import axios from "axios";
import {
  TextField,
  MenuItem,
  Button,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListSubheader,
  Divider
} from "@material-ui/core";
import { Form, Field } from "react-final-form";

function App() {
  const [inTraffic, setInTraffic] = useState(0);
  const [outTrafic, setOutTrafic] = useState(0);
  const [inErrors, setInErrors] = useState(0);
  const [outErrors, setOutErrors] = useState(0);
  const [interfaces, setInterfaces] = useState([]);
  const [maxIn, setMaxIn] = useState(false);
  const [maxOut, setMaxOut] = useState(false);
  const setVariables = async newVariables => {
    const response = await axios.post("http://127.0.0.1:5002/change-params", {
      method: "POST",
      mode: "no-cors",
      data: newVariables,
      headers: {
        "Access-Control-Allow-Origin": "127.0.0.1",
        "Content-Type": "application/json",
        "Access-Control-Allow-Headers": "Content-Type"
      }
    });
    console.log("response", response.data);
  };

  const getData = async () => {
    try {
      const response = await axios.get("http://127.0.0.1:5002/trafego", {
        method: "GET",
        mode: "no-cors",
        headers: {
          "Access-Control-Allow-Origin": "127.0.0.1",
          "Content-Type": "application/json",
          "Access-Control-Allow-Headers": "Content-Type"
        }
      });
      console.log("response", response.data);

      setInTraffic(response.data["trafego-entrada"]);
      setOutTrafic(response.data["trafego-saida"]);
      setInErrors(response.data["erros-entrada"]);
      setOutErrors(response.data["errors-saida"]);
      setInterfaces(response.data["interfaces"]);
      setMaxIn(response.data["maxTrafficBoolIn"]);
      setMaxOut(response.data["maxTrafficBoolOut"]);
    } catch (err) {
      console.warn("ERROR:", err);
    }
  };

  useEffect(() => {
    setInterval(() => {
      getData();
    }, 1000);
  }, []);

  return (
    <div className="App">
      <div className="entrada-dados-card">
        <Form
          initialValues={{
            host: "",
            commnity: "",
            snmpUser: "",
            authProtocol: "MD5",
            authPass: "",
            securityLevel: "auth_without_privacy",
            privacyProtocol: "DEFAULT",
            privacyPass: "",
            maxTraffic: 5 * 10 ** 6
          }}
          onSubmit={setVariables}
          // validate={validate}
          render={({ handleSubmit }) => (
            <>
              <Field
                name="host"
                render={({ meta, input }) => (
                  <TextField
                    label="Host"
                    placeholder="Ex: 127.0.0.1"
                    // margin="normal"
                    variant="outlined"
                    {...meta}
                    {...input}
                  />
                )}
              />
              <Field
                name="commnity"
                render={({ meta, input }) => (
                  <TextField
                    label="Commnity"
                    placeholder="Ex: public"
                    // margin="normal"
                    variant="outlined"
                    {...meta}
                    {...input}
                  />
                )}
              />
              <Field
                name="snmpUser"
                render={({ meta, input }) => (
                  <TextField
                    label="SNMP User"
                    placeholder="Ex: MD5User"
                    // margin="normal"
                    variant="outlined"
                    {...meta}
                    {...input}
                  />
                )}
              />

              <Field
                name="authProtocol"
                render={({ meta, input }) => (
                  <TextField
                    select
                    label="Auth Protocol"
                    // margin="normal"
                    variant="outlined"
                    {...meta}
                    {...input}
                  >
                    <MenuItem key={"MD5"} value={"MD5"}>
                      MD5
                    </MenuItem>
                    <MenuItem key={"SHA"} value={"SHA"}>
                      SHA
                    </MenuItem>
                  </TextField>
                )}
              />

              <Field
                name="authPass"
                render={({ meta, input }) => (
                  <TextField
                    label="Auth Password"
                    placeholder="Ex: 'The Net-SNMP Demo Password'"
                    // margin="normal"
                    variant="outlined"
                    {...meta}
                    {...input}
                  />
                )}
              />

              <Field
                name="securityLevel"
                render={({ meta, input }) => (
                  <TextField
                    select
                    label="Security Level"
                    // margin="normal"
                    variant="outlined"
                    {...meta}
                    {...input}
                  >
                    <MenuItem
                      key={"auth_without_privacy"}
                      value={"auth_without_privacy"}
                    >
                      auth_without_privacy
                    </MenuItem>
                    <MenuItem
                      key={"no_auth_or_privacy"}
                      value={"no_auth_or_privacy"}
                    >
                      no_auth_or_privacy
                    </MenuItem>
                    <MenuItem
                      key={"auth_with_privacy"}
                      value={"auth_with_privacy"}
                    >
                      auth_with_privacy
                    </MenuItem>
                  </TextField>
                )}
              />
              <Field
                name="privacyProtocol"
                render={({ meta, input }) => (
                  <TextField
                    select
                    label="Privacy Protocol"
                    // margin="normal"
                    variant="outlined"
                    {...meta}
                    {...input}
                  >
                    <MenuItem key={"DEFAULT"} value={"DEFAULT"}>
                      DEFAULT
                    </MenuItem>
                    <MenuItem key={"DES"} value={"DES"}>
                      DES
                    </MenuItem>
                    <MenuItem key={"AES"} value={"AES"}>
                      AES
                    </MenuItem>
                  </TextField>
                )}
              />
              <Field
                name="privacyPass"
                render={({ meta, input }) => (
                  <TextField
                    label="Privacy Password"
                    // margin="normal"
                    variant="outlined"
                    {...meta}
                    {...input}
                  />
                )}
              />

              <Field
                name="maxTraffic"
                render={({ meta, input }) => (
                  <TextField
                    label="Max Traffic - bytes/sec"
                    placeholder="bytes/sec"
                    // margin="normal"
                    variant="outlined"
                    {...meta}
                    {...input}
                  />
                )}
              />
              <Button
                onClick={handleSubmit}
                variant="outlined"
                className="button"
                color="primary"
              >
                Update
              </Button>
            </>
          )}
        />
      </div>

      <div className="status-card">
        <div className="cell">
          <div className="cell-body">
            <TextField
              label="Traffic IN"
              margin="normal"
              variant="outlined"
              error={maxIn}
              value={`${inTraffic} bytes/s`}

            />
            <TextField
              label="Traffic OUT"
              margin="normal"
              variant="outlined"
              error={maxOut}
              value={`${outTrafic} bytes/s`}
            />
          </div>
        </div>
        <div className="cell">
          <div className="cell-body">
            <TextField
              label="Erros IN"
              margin="normal"
              variant="outlined"
              value={`In ${inErrors}`}
            />
            <TextField
              label="Erros OUT"
              margin="normal"
              variant="outlined"
              value={`Out ${outErrors}`}
            />
          </div>
        </div>
        <div className="cell">
          <Paper>
            <List
              subheader={
                <ListSubheader component="div" id="nested-list-subheader">
                  Interfaces
                </ListSubheader>
              }
            >
              {interfaces.map(interf => (
                <>
                  <Divider />
                  <ListItem>
                    <ListItemText primary={`${interf.name}: ${interf.state}`} />
                  </ListItem>
                </>
              ))}
            </List>
          </Paper>
        </div>
      </div>
    </div>
  );
}

export default App;
